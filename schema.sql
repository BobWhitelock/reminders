drop table if exists reminder;
create table reminder (
    id integer primary key autoincrement,
    name text not null,
    time datetime not null
);