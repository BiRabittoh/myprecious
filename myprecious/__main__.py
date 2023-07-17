from flask import Flask, request, render_template, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from contextlib import suppress
from Db import init_db, get_user_from_username, get_user_from_id, add_user_to_queue
import os, json, base64
import Constants as c
if c.DEBUG_SWITCH:
    from GamesApiTest import search_game
else:
    from GamesApi import search_game

app = Flask(__name__)
login_manager = LoginManager(app)

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

def handle_response(response):
    return [ [ handle_platform(game, platform) for platform in game["platforms"] ] for game in response ]

def collapse_list_of_lists(l):
    return [ item for sublist in l for item in sublist ]

@login_manager.user_loader
def load_user(user_id):
    lu = get_user_from_id(user_id)
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

    r = get_user_from_username(username)
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

@app.route('/register', methods=['GET', 'POST'])
def route_register():
    if current_user.is_authenticated:
        return redirect('/')
    
    if request.method == "GET":
        return render("register.html")
    
    form = request.form
    username = form["username"].lower()
    email = form["email"].lower()
    password = form["password"]

    if len(password) < c.MIN_PW_LENGTH or len(username) < c.MIN_USERNAME_LENGTH:
        return render_template("register.html", user=current_user, error="Your username or password is too short.")
    
    if len(password) > c.MAX_LENGTH or len(username) > c.MAX_LENGTH:
        return render_template("register.html", user=current_user, error="Your username or password is too long.")
    
    res = add_user_to_queue(username, password, email)
    if res == None:
        return render_template("register.html", user=current_user, error="This username is already registered.")
    return render("register_done.html")

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
    
    games = collapse_list_of_lists(handle_response(search_response))
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


@app.route('/admin', methods=['GET', 'POST'])
def route_admin():
    if not current_user.is_authenticated:
        return redirect('/')
    
    if current_user.id != 1:
        return redirect('/')
    
    if request.method == "GET":
        return render("admin.html")
    
    return render("admin.html")

@app.route('/about')
def route_about():
    return render("about.html")

if __name__ == "__main__":
    app.debug=c.DEBUG_SWITCH
    app.secret_key = c.SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'
    init_db()
    app.run(port=1111)
