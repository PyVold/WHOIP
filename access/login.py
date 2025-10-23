"""
User authentication and token management module.
Handles login, logout, and API token creation.
"""
from flask import Flask, render_template, request, redirect, session, Blueprint, url_for, flash, current_app
from flask_login import UserMixin, login_user, logout_user, current_user, login_required, LoginManager
from urllib.parse import urlparse, urljoin
from . import access_app
from . import User, Application, db
import secrets
from werkzeug.security import check_password_hash
from utils import validate_app_name, sanitize_string
import logging

logger = logging.getLogger(__name__)


def is_safe_url(target):
    """
    Check if redirect URL is safe to prevent open redirect vulnerabilities.

    Args:
        target: URL to validate

    Returns:
        True if URL is safe, False otherwise
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


@access_app.route('/login/', methods=['GET', 'POST'])
def login():
    """
    User login endpoint.

    GET: Display login form
    POST: Process login credentials
    """
    if request.method == 'POST':
        username = sanitize_string(request.form.get('username', ''), 50)
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.')
            return redirect(url_for('access.login'))

        user = User.lookup(username=username)
        if not user:
            logger.warning(f"Failed login attempt for non-existent user: {username}")
            flash('Invalid username or password.')
            return redirect(url_for('access.login'))
        elif not check_password_hash(user.password, password):
            logger.warning(f"Failed login attempt for user: {username}")
            flash('Invalid username or password.')
            return redirect(url_for('access.login'))
        else:
            login_user(user)
            logger.info(f"User logged in: {username}")

            # Handle redirect to next page
            if ('next' in session) and ('logout' not in session):
                next_url = session['next']
                if is_safe_url(next_url):
                    return redirect(next_url)

            return redirect(url_for('access.tokens'))

    if request.args.get('next'):
        session['next'] = request.args.get('next')

    return render_template('login.html')


@access_app.route('/')
@access_app.route('/tokens/', methods=['GET', 'POST'])
@login_required
def tokens():
    """
    Token management dashboard.

    GET: Display user's API tokens
    POST: Create new API token
    """
    # Use current_user.applications instead of redundant query
    fetch_apps = current_user.applications
    max_apps = current_app.config.get('MAX_APPS_PER_USER', 3)

    if request.method == 'GET':
        # Build apps dictionary with comprehension instead of loop
        apps = {
            app.app_name: [app.token, app.id, app.state, app.calls_count, app.max_calls]
            for app in fetch_apps
        } if fetch_apps else {'None': ['None', 0, 'N/A', 0, 0]}

        return render_template('tokens.html', apps=apps, max_apps=max_apps)

    if request.method == 'POST':
        # Check app limit
        if len(fetch_apps) >= max_apps:
            flash(f'You have already registered the maximum number of applications ({max_apps})!')
            return redirect(url_for('access.tokens'))

        # Get and validate app name
        appname = sanitize_string(request.form.get('appname', ''), 100)

        is_valid, error_msg = validate_app_name(appname)
        if not is_valid:
            flash(error_msg)
            return redirect(url_for('access.tokens'))

        # Check for duplicate app name
        for existing_app in fetch_apps:
            if appname.lower() == existing_app.app_name.lower():
                flash('This application name is already registered!')
                return redirect(url_for('access.tokens'))

        try:
            # Generate secure token
            token = secrets.token_hex(32)  # 64 character token (more secure)

            # Create new application
            new_app = Application(
                app_name=appname,
                user_id=current_user.id,
                token=token,
                max_calls=current_app.config.get('DEFAULT_RATE_LIMIT', 1000)
            )
            db.session.add(new_app)
            db.session.commit()

            logger.info(f"New application created: {appname} by user {current_user.username}")
            flash(f'Application "{appname}" created successfully! Token is waiting for approval.')
            return redirect(url_for('access.tokens'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating application: {e}")
            flash('An error occurred while creating the application. Please try again.')
            return redirect(url_for('access.tokens'))


@access_app.route('/logout/')
@login_required
def logout():
    """User logout endpoint."""
    logger.info(f"User logged out: {current_user.username}")
    logout_user()
    session.clear()  # Clear all session data
    flash('You have been logged out successfully.')
    return redirect(url_for('access.login'))