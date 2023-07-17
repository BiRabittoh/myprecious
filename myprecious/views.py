from myprecious import app, login_manager
from flask import request, redirect, render_template
from flask_login import login_user, logout_user, current_user
import myprecious.constants as c
from myprecious.utils import handle_response, parse_remember
from myprecious.auth import handle_register, handle_login, get_logged_user
from myprecious.files import handle_upload
from myprecious.encoding import obj_decode
if app.debug:
    from myprecious.games_api_test import search_game
else:
    from myprecious.games_api import search_game

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
        return render("done.html", text="Your registration request has been taken into account and will likely be processed in a few days.")
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
    games = handle_response(search_response)
    return render("search.html", games=games, query=query)

@app.route('/upload', methods=['GET', 'POST'])
def route_upload():
    if not current_user.is_authenticated:
        return redirect('/login')
    if request.method == 'GET':
        info = request.args.get("info")
        if info is None:
            return render("upload.html", game=c.NO_GAME)
        return render("upload.html", game=obj_decode(info))
    
    error = handle_upload(request, current_user.id)
    if error is None:
        return render("done.html", text="Your save file was uploaded correctly.")
    return render("input.html", error=error)


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
