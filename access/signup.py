from flask_login import UserMixin, login_user, logout_user, current_user, login_required, LoginManager
from flask import Flask, render_template, request, redirect, session, Blueprint, url_for, flash
from . import access_app as signup_app
from . import db, User
from werkzeug.security import generate_password_hash


@signup_app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method=='GET': 
        return render_template('signup.html')
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        usercheck = User.query.filter_by(username=username).first() 
        emailcheck = User.query.filter_by(email=email).first() 
        if usercheck:
            flash('Username is not Available!')
            return redirect(url_for('access.signup'))
        if emailcheck:
            flash('This email address is already registered!')
            return redirect(url_for('access.signup'))
        if not password:
            flash('Please enter a password!')
            return redirect(url_for('access.signup'))
        #token = secrets.token_hex(16)
        new_user = User(username=username, name=name, email=email,\
                        password=generate_password_hash(password, \
                        method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('access.login'))