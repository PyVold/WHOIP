"""
User registration module with input validation and secure password hashing.
"""
from flask_login import UserMixin, login_user, logout_user, current_user, login_required, LoginManager
from flask import Flask, render_template, request, redirect, session, Blueprint, url_for, flash, current_app
from . import access_app as signup_app
from . import db, User
from werkzeug.security import generate_password_hash
from utils import validate_email, validate_password, validate_username, sanitize_string
import logging

logger = logging.getLogger(__name__)


@signup_app.route('/signup/', methods=['GET', 'POST'])
def signup():
    """
    User registration endpoint.

    GET: Display registration form
    POST: Process registration with validation
    """
    if request.method == 'GET':
        return render_template('signup.html')

    # Get and sanitize form data
    username = sanitize_string(request.form.get('username', ''), 50)
    email = sanitize_string(request.form.get('email', ''), 100)
    name = sanitize_string(request.form.get('name', ''), 100)
    password = request.form.get('password', '')

    # Validate username
    is_valid, error_msg = validate_username(username)
    if not is_valid:
        flash(error_msg)
        return redirect(url_for('access.signup'))

    # Validate email
    if not validate_email(email):
        flash('Please enter a valid email address!')
        return redirect(url_for('access.signup'))

    # Validate password
    is_valid, error_msg = validate_password(password, current_app.config)
    if not is_valid:
        flash(error_msg)
        return redirect(url_for('access.signup'))

    # Validate name
    if not name or len(name) < 2:
        flash('Please enter your full name (at least 2 characters)!')
        return redirect(url_for('access.signup'))

    # Check if username already exists
    usercheck = User.query.filter_by(username=username).first()
    if usercheck:
        flash('Username is not available!')
        return redirect(url_for('access.signup'))

    # Check if email already exists
    emailcheck = User.query.filter_by(email=email).first()
    if emailcheck:
        flash('This email address is already registered!')
        return redirect(url_for('access.signup'))

    try:
        # Create new user with secure password hashing (pbkdf2:sha256 with 600k iterations)
        new_user = User(
            username=username,
            name=name,
            email=email,
            password=generate_password_hash(
                password,
                method='pbkdf2:sha256:600000'
            )
        )
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user registered: {username}")
        flash('Registration successful! Please log in.')
        return redirect(url_for('access.login'))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during user registration: {e}")
        flash('An error occurred during registration. Please try again.')
        return redirect(url_for('access.signup'))