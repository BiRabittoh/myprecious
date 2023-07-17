import myprecious.constants as c
from myprecious.db import add_user_to_queue, get_user_from_username, get_user_from_id
from flask_login import UserMixin

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

def handle_register(form):
    username = form["username"].lower()
    email = form["email"].lower()
    password = form["password"]

    if len(password) < c.MIN_PW_LENGTH or len(username) < c.MIN_USERNAME_LENGTH:
        return "Your username or password is too short."
    
    if len(password) > c.MAX_LENGTH or len(username) > c.MAX_LENGTH:
        return "Your username or password is too long."
    
    res = add_user_to_queue(username, password, email)
    if res == None:
        return "This username is already registered."
    return None

def handle_login(form):
    username = form["username"].lower()
    password = form["password"]
    
    r = get_user_from_username(username)
    if r is None:
        return "That account does not exist.", { "username": username }
    user = construct_user(r[0], r[1], r[2], r[3])

    last_user = { "username": username }
    if user is None:
        return "Parsing error.", last_user
    
    if user.password == password:
        return None, user
    return "Wrong password.", last_user

def get_logged_user(user_id):
    lu = get_user_from_id(user_id)
    if lu is None:
        return None
    return construct_user(lu[0], lu[1], lu[2], lu[3])