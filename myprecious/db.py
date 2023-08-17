
import os, uuid, sqlite3
from base64 import b64encode
from contextlib import suppress
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import myprecious.constants as c

ph = PasswordHasher()

def get_hashable(password: str, salt: str):
    return password + salt + c.SECRET_KEY

def verify_user(username, hash, password, salt):
    hashable = get_hashable(password, salt)
    try:
        ph.verify(hash, hashable)
    except VerifyMismatchError:
        return False

    if ph.check_needs_rehash(hash):
        new_hash = ph.hash(hashable)
        query_str = "UPDATE login SET password = (?) WHERE username = (?);"
        db_query(query_str, [new_hash, username])
    return True

def db_query(query, parameters):
    with sqlite3.connect(c.DB_PATH) as db_connection:
        curs = db_connection.cursor()
        curs.execute(query, parameters)
        return curs

def db_query_one(query, parameters):
        curs = db_query(query, parameters)
        try:
            return list(curs.fetchone())
        except TypeError:
            return None
        
def run_sql(sql_path: str):
    with open(sql_path, 'r', encoding="utf-8") as f:
        with sqlite3.connect(c.DB_PATH) as con:
            curs = con.cursor()
            sql = f.read()
            curs.executescript(sql)

def add_user_to_queue(username, password, email, salt=None):
    if get_user_from_username(username) is not None:
        return "registered"
    if get_user_from_username(username, "queue") is not None:
        return "queued"
    add_user(username, password, email, salt, "queue")
    return "done"

def add_user(username, password, email, salt=None, table="login", hashed=False):
    if salt is None:
        salt = b64encode(os.urandom(12)).decode('utf-8')
    query_str = f"insert or ignore into { table } (username, password, salt, email) values (?,?,?,?);"
    if not hashed:
        password = ph.hash(get_hashable(password, salt))
    query_param = [username, password, salt, email]
    return db_query(query_str, query_param)

def get_user_from_username(username: str, table="login"):
    return db_query_one(f"SELECT * FROM { table } where username = (?);", [username])

def get_user_from_id(id: int):
    return db_query_one("SELECT * from login where user_id = (?);", [id])

def get_queued_users():
    res = db_query("SELECT * from queue;", [])
    return res.fetchall()

def deny_user(nick):
    return db_query_one("DELETE FROM queue WHERE username = (?)", [nick])

def allow_user(nick):
    r = get_user_from_username(nick, "queue")
    r = add_user(r[0], r[1], r[3], r[2], hashed=True)
    return deny_user(nick)

def init_db():
    with suppress(FileExistsError):
        os.makedirs(c.BASE_DIRECTORY)
    run_sql(c.MIGRATIONS_INIT_PATH)
    add_user(c.DEFAULT_ADMIN_USER, c.DEFAULT_ADMIN_PW, c.DEFAULT_ADMIN_EMAIL)
