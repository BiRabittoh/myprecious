insert or ignore into
    login
        (username, password, email)
    values
        ('user', 'password', 'user@email.com'),
        ('alice', 'alice', null),
        ('bob', 'bob', null);
