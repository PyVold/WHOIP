"""
WHOIP - IP Geolocation and WHOIS Service
Main application module with Flask setup and configuration.
"""
from flask import Flask, redirect, url_for
from flask_login import current_user
from resources import api, blueprint
from access import access_app, db, User, Application
from access import login_manager
from werkzeug.middleware.proxy_fix import ProxyFix
import os
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from logbase import call_logger, setup_logger
from config import get_config

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Initialize logging
call_logger()

# Create Flask application
app = Flask(__name__)

# Load configuration from config.py
config_class = get_config()
app.config.from_object(config_class)

# Validate production config
if os.getenv('FLASK_ENV') == 'production':
    try:
        config_class.validate()
    except ValueError as e:
        raise RuntimeError(f"Configuration validation failed: {e}")

# Setup proxy fix for proper IP address handling behind reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'access.login'
login_manager.login_message = 'Please log in to access this page.'


class SecureAdminIndexView(AdminIndexView):
    """Custom admin index view that requires authentication."""

    def is_accessible(self):
        """Check if current user is authenticated and is admin."""
        if not current_user.is_authenticated:
            return False
        return current_user.username in app.config['ADMIN_USERS']

    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login page if user doesn't have access."""
        return redirect(url_for('access.login', next='/admin'))


class SecureModelView(ModelView):
    """Custom model view that requires admin authentication."""

    def is_accessible(self):
        """Check if current user is authenticated and is admin."""
        if not current_user.is_authenticated:
            return False
        return current_user.username in app.config['ADMIN_USERS']

    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login page if user doesn't have access."""
        return redirect(url_for('access.login', next='/admin'))


# Setup Flask-Admin with security
admin = Admin(
    app,
    name='WHOIP Admin Panel',
    template_mode='bootstrap3',
    index_view=SecureAdminIndexView()
)
admin.add_view(SecureModelView(User, db.session, name='Users'))
admin.add_view(SecureModelView(Application, db.session, name='API Tokens'))

# Register blueprints
app.register_blueprint(blueprint)
app.register_blueprint(access_app)


@app.route('/')
def index():
    """Root endpoint - redirect to API documentation."""
    return redirect('/api/')


@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    from datetime import datetime

    return {
        'status': 'healthy',
        'service': 'WHOIP',
        'version': app.config['API_VERSION'],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }, 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return {
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'documentation': '/api/'
    }, 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return {
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'documentation': '/api/'
    }, 500


if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Run application
    port = int(os.getenv('PORT', '5500'))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=app.config['DEBUG']
    )