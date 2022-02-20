from flask import Blueprint
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

access_app = Blueprint('access', __name__, template_folder='templates', url_prefix='/myapi')



login_manager = LoginManager()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    applications = db.relationship("Application", back_populates="username")

    def __repr__(self):
        return self.username

class Application(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    app_name = db.Column(db.String(100))
    user_id = db.Column(db.ForeignKey('user.id'))
    username = db.relationship("User", back_populates="applications")
    token = db.Column(db.String(1000))
    state = db.Column('state', db.Enum('active', 'waiting approval', 'Not Active', name='token_status'), server_default='waiting approval')

    def __repr__(self):
        return self.app_name
        
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from . import login, signup, delete