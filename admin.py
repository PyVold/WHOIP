from email.mime import application
from flask import Flask
from resources import api, blueprint
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.abspath('') + '/lite.db'
app.config['SECRET_KEY'] = 'mysecret'

db = SQLAlchemy(app)
admin = Admin(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True)
    password = 
    applications = db.relationship('Application')

    def __repr__(self):
        return self.username
        
class UserView(ModelView):
    form_columns = ['username']

class Application(db.Model):
    app_id = db.Column(db.Integer, primary_key = True)
    app_name = db.Column(db.String(30))
    user_id = db.Column(db.String(30), db.ForeignKey('user.id'))
    token_key = db.Column(db.String(100))
    username = db.relationship('User')

    def __repr__(self):
        return self.app_name
class ApplicationView(ModelView):
    form_columns = ['app_name', 'username']

app.register_blueprint(blueprint)
admin.add_view(UserView(User, db.session))
admin.add_view(ApplicationView(Application, db.session))

if __name__ == '__main__':
    # debug mode has to be turned off in production, it's only for testing.
    app.run(host = "0.0.0.0", port = "5500")