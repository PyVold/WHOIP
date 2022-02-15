import imp
from flask import Blueprint
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

auth_app = Blueprint('access', __name__, template_folder='templates')