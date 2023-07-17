from flask import Flask, request, render_template, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from contextlib import suppress
import os, json, base64, sqlite3
import hashlib, uuid
import Constants as c
if c.DEBUG_SWITCH:
    from GamesApiTest import search_game
else:
    from GamesApi import search_game

app = Flask(__name__)
login_manager = LoginManager(app)

def hash(password: str):
    salt = uuid.uuid4().hex
    return hashlib.sha512(password + salt).hexdigest(), salt

def db_query_one(query, parameters):
    with sqlite3.connect(c.DB_PATH) as db_connection:
        curs = db_connection.cursor()
        curs.execute(query, parameters)
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

def add_user(username, password, email):
    query_str = "insert or ignore into login (username, password, email) values (?,?,?);"
    query_param = [username, password, email]
    return db_query_one(query_str, query_param)

def init_db():
    run_sql(c.MIGRATIONS_INIT_PATH)
    add_user(c.DEFAULT_ADMIN_USER, c.DEFAULT_ADMIN_PW, c.DEFAULT_ADMIN_EMAIL)


class User(UserMixin):
    def __init__(self, user_id, username, password, email):
        self.id = user_id
        self.username = username
        self.password = password
        self.email = email

def construct_user(id, username, password, email):
    try:
        return User(int(id), username, password, email)
    except TypeError:
        return None
    
def render(template):
    return render_template(template, user=current_user)


def handle_platform(game, platform):
    try:
        game_cover = "https:" + game["cover"]["url"]
    except KeyError:
        game_cover = c.MISSING_COVER_URL
    temp_obj = {
        "game_id": game["id"],
        "platform_id": platform["id"],
        "cover": game_cover,
        "title": game["name"],
        "platform": platform["name"]
    }
    temp_json = json.dumps(temp_obj)
    temp_bytes = temp_json.encode("utf-8")
    temp_base64 = base64.b64encode(temp_bytes)
    temp_obj["info"] = temp_base64.decode("utf-8")
    return temp_obj

def handle_game(game):
    return [ handle_platform(game, platform) for platform in game["platforms"] ]

def collapse_list_of_lists(l):
    return [ item for sublist in l for item in sublist ]

@login_manager.user_loader
def load_user(user_id):
    lu = db_query_one("SELECT * from login where user_id = (?)", [user_id])
    if lu is None:
        return None
    return construct_user(lu[0], lu[1], lu[2], lu[3])

@app.route('/')
def route_index():
    return render("index.html")

@app.route('/login', methods=['GET', 'POST'])
def route_login():
    if current_user.is_authenticated:
        return redirect('/')
    
    if request.method == "GET":
        return render("login.html")
    
    form = request.form
    username = form["username"].lower()
    password = form["password"]
    try:
        remember = bool(form["remember"])
    except KeyError:
        remember = False

    r = db_query_one("SELECT * FROM login where username = (?)", [username])
    if r is None:
        return render_template("login.html", user=current_user, last_user=username)
    user = construct_user(r[0], r[1], r[2], r[3])

    if user is None:
        return redirect(url_for("login"))
    
    if user.password == password:
        login_user(user, remember=remember)
        return redirect("/")
    else:
        return render_template("login.html", user=current_user, last_user=username)

@app.route('/logout')
def route_logout():
    logout_user()
    return redirect("/")

@app.route('/search', methods=['GET', 'POST'])
def route_search():
    if not current_user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        return render("search.html")
    
    query = request.form["query"]
    search_response = search_game(query)
    
    games = collapse_list_of_lists([ handle_game(x) for x in search_response ])
    return render_template("search.html", user=current_user, games=games, query=query)

@app.route('/upload', methods=['GET', 'POST'])
def route_upload():
    if not current_user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        info = request.args.get("info")
        if info is None:
            return render_template("upload.html", user=current_user, game=c.NO_GAME)
        # info = base64
        base64_bytes = info.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('utf-8')
        game = json.loads(message)
        return render_template("upload.html", user=current_user, game=game)
        
    f = request.files['file']
    try:
        game_id = int(request.form['game_id'])
        platform_id = int(request.form['platform_id'])
    except ValueError:
        return redirect("/upload")
    
    # TODO: use IGDB api to validate game_id, platform_id and title before adding
    # TODO: save game in DB

    save_folder = os.path.join(c.BASE_DIRECTORY, c.CONTENT_DIRECTORY, str(current_user.id), str(game_id), str(platform_id))
    with suppress(FileExistsError):
        os.makedirs(save_folder)
    if f.filename is None:
        return redirect("/upload")
    save_file = os.path.join(save_folder, secure_filename(f.filename))
    f.save(save_file)
    return render("index.html")

if __name__ == "__main__":
    app.debug=c.DEBUG_SWITCH
    app.secret_key = c.SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'
    init_db()
    app.run(port=1111)
