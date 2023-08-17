import myprecious.constants as c
from myprecious.db import add_user_to_queue, get_user_from_username, get_user_from_id, verify_user
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, username, password, salt, email):
        self.id = user_id
        self.username = username
        self.password = password
        self.salt = salt
        self.email = email

def construct_user(row):
    try:
        return User(int(row[0]), row[1], row[2], row[3], row[4])
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
    match res:
        case "registered":
            return "This user is already registered."
        case "queued":
            return "This user is waiting for approval."
        case "done":
            return "Done! Your request was submitted and will hopefully be approved shortly."
        case _:
            return "An error as occurred."
        
    return None

def handle_login(form):
    username = form["username"].lower()
    password = form["password"]
    
    r = get_user_from_username(username)
    if r is None:
        return "This account either does not exist or it's still awaiting approval.", { "username": username }
    user = construct_user(r)

    last_user = { "username": username }
    if user is None:
        return "Parsing error.", last_user
    if verify_user(username, user.password, password, user.salt):
        return None, user
    return "Wrong password.", last_user

def get_logged_user(user_id):
    lu = get_user_from_id(user_id)
    if lu is None:
        return None
    return construct_user(lu)
