import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/tmp/reminders.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def view_reminders():
    cur = g.db.execute('select name, time from reminder order by time desc')
    reminders = [dict(name=row[0], time=row[1]) for row in cur.fetchall()]
    return render_template('view_reminders.html', reminders=reminders)


@app.route('/add', methods=['POST'])
def add_reminder():
    if not session.get('logged_in'):
        abort(401) # unauthorized
    g.db.execute('insert into reminder (name, time) values (?, ?)',
                 [request.form['name'], request.form['time']])
    g.db.commit()
    flash('New reminder successfully added.')
    return redirect(url_for('view_reminders'))


@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.form['username'] != app.config['USERNAME']:
        error = 'Invalid username'
    elif request.form['password'] != app.config['PASSWORD']:
        error = 'Invalid password'
    else:
        session['logged_in'] = True
        flash('You were logged in')
        return redirect(url_for('view_reminders'))
    return render_template('login.html', error=error) # TODO change so error renders on main page


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('view_reminders'))


if __name__ == '__main__':
    app.run()