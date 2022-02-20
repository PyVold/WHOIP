from flask import Flask
from resources import api, blueprint
from access import access_app, db, User, Application
from access import login_manager
from werkzeug.middleware.proxy_fix import ProxyFix
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.abspath('') + '/lite2.db'
app.config['SECRET_KEY'] = 'mysecret'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'


db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'access.login'


admin = Admin(app, name='MyIP API admin panel', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Application, db.session))


app.register_blueprint(blueprint)
app.register_blueprint(access_app)


if __name__ == '__main__':
    # debug mode has to be turned off in production, it's only for testing.
    app.run(host = "0.0.0.0", port = "5500", debug=False)