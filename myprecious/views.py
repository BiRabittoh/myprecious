from myprecious import app, login_manager
from flask import request, redirect, render_template
from flask_login import login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from contextlib import suppress
import myprecious.Constants as c
from myprecious.Utils import handle_response, parse_remember
from myprecious.Auth import handle_register, handle_login, get_logged_user
from myprecious.Encoding import obj_decode
import os
if c.DEBUG_SWITCH:
    from myprecious.GamesApiTest import search_game
else:
    from myprecious.GamesApi import search_game

def render(template, **context):
    return render_template(template, user=current_user, **context)

@login_manager.user_loader
def load_user(user_id):
    return get_logged_user(user_id)

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
    remember = parse_remember(form)
    
    error, user = handle_login(request.form)
    if error is None:
        login_user(user, remember=remember)
        return redirect("/")
    last_user = user.username if user else None
    return render("login.html", last_user=last_user, error=error)
    

@app.route('/register', methods=['GET', 'POST'])
def route_register():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == "GET":
        return render("register.html")
    error = handle_register(request.form)
    if error is None:
        return render("register_done.html")
    return render("register.html", error=error)
    
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
    return render("search.html", games=handle_response(search_response), query=query)

@app.route('/upload', methods=['GET', 'POST'])
def route_upload():
    if not current_user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        info = request.args.get("info")
        if info is None:
            return render("upload.html", game=c.NO_GAME)
        game = obj_decode(info)
        return render("upload.html", game=game)
        
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
