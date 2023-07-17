
import uuid, hashlib, sqlite3
import myprecious.Constants as c

def hash(password: str):
    salt = uuid.uuid4().hex
    return hashlib.sha512(password + salt).hexdigest(), salt

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

def add_user_to_queue(username, password, email):
    res = get_user_from_username(username)
    if res is not None:
        return None
    query_str = "insert or ignore into queue (username, password, email) values (?,?,?);"
    query_param = [username, password, email]
    return db_query(query_str, query_param)

def add_user(username, password, email):
    query_str = "insert or ignore into login (username, password, email) values (?,?,?);"
    query_param = [username, password, email]
    return db_query(query_str, query_param)

def accept_user(username):
    r = get_user_from_username(username, "queue")
    return add_user(r[0], r[1], r[2])

def get_user_from_username(username: str, table="login"):
    return db_query_one(f"SELECT * FROM { table } where username = (?)", [username])

def get_user_from_id(id: int):
    return db_query_one("SELECT * from login where user_id = (?)", [id])

def init_db():
    run_sql(c.MIGRATIONS_INIT_PATH)
    add_user(c.DEFAULT_ADMIN_USER, c.DEFAULT_ADMIN_PW, c.DEFAULT_ADMIN_EMAIL)
