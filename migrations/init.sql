create table if not exists login (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username text unique not null,
    password text not null,
    salt text not null,
    email text
);

create table if not exists queue (
    username text primary key,
    password text not null,
    salt text not null,
    email text,
    requested datetime DEFAULT CURRENT_TIMESTAMP
)
