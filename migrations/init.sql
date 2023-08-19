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
);

create table if not exists platforms (
    platform_id INTEGER PRIMARY KEY,
    name text unique not null
);

create table if not exists games (
    game_id INTEGER PRIMARY KEY,
    title text not null
);

create table if not exists saves (
    user_id integer not null,
    game_id integer not null,
    platform_id integer not null,
    filename text not null,
    primary key (user_id, game_id, platform_id)
);
