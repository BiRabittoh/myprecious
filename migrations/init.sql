create table if not exists login (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username text unique not null,
    password text not null,
    email text
);
