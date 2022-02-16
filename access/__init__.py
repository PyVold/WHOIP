from flask import Blueprint
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
<<<<<<< HEAD

auth_app = Blueprint('access', __name__, template_folder='templates')
=======

access_app = Blueprint('access', __name__, template_folder='templates', url_prefix='/myapi/')


login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    token = db.Column(db.String(1000), unique=True)

    def __repr__(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from . import login, signup
>>>>>>> 643ce810a5ba7d4669e13b1bec079dc42d1e027e
