from flask import Flask
from resources import api, blueprint
from access import auth_app, db
from access.login import login_manager
from werkzeug.middleware.proxy_fix import ProxyFix
import os


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.abspath('') + '/lite.db'
app.config['SECRET_KEY'] = 'mysecret'

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'access.login'

app.register_blueprint(blueprint)
app.register_blueprint(auth_app)


if __name__ == '__main__':
    # debug mode has to be turned off in production, it's only for testing.
    app.run(host = "0.0.0.0", port = "5500")