from flask import Flask
from flask_login import LoginManager
import myprecious.Constants as c
from myprecious.Db import init_db

app = Flask(__name__)
login_manager = LoginManager(app)

app.debug=c.DEBUG_SWITCH
app.secret_key = c.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
init_db()

import myprecious.views
