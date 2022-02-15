import imp
from flask import Blueprint
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
auth_app = Blueprint('auth', __name__, template_folder='templates')

#auth_app.register_blueprint(access_app)
#auth_control.register_blueprint(signup_app)