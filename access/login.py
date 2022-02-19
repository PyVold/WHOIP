from flask import Flask, render_template, request, redirect, session, Blueprint, url_for, flash
from flask_login import UserMixin, login_user, logout_user, current_user, login_required, LoginManager
from urllib.parse import urlparse, urljoin
from . import access_app
from . import User, Application, db
import secrets
from werkzeug.security import check_password_hash


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@access_app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User does not exist!')
            return redirect(url_for('access.login'))
        elif not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('access.login'))
        else:
            login_user(user)
            if ('next' in session) and ('logout' not in session):
                next = session['next']
                if is_safe_url(next):
                    return redirect(next)
            return redirect(url_for('access.tokens'))
    if request.args.get('next'):
        session['next'] = request.args.get('next')
    return render_template('login.html')
    

@access_app.route('/')
@access_app.route('/tokens/', methods=['GET', 'POST'])
@login_required
def tokens():
    fetch_apps = User.query.filter_by(username=current_user.username).first().applications
    if request.method == 'GET':
        apps = {}
        if len(fetch_apps) != 0:
            for each_app in fetch_apps:
                apps[each_app.app_name] = [each_app.token, each_app.id, each_app.state]
        else:
            apps['None'] = ['None', 0] 
        return render_template('tokens.html', apps=apps)

    if request.method == 'POST':
        if len(fetch_apps) >= 3:
            flash('You already registered the max number of apps!')
            return redirect(url_for('access.tokens'))
        appname = request.form['appname']
        for each_app in fetch_apps:
            if appname == each_app.app_name:
                flash('This application is already registered!')
                return redirect(url_for('access.tokens'))
        token = secrets.token_hex(16)
        new_app = Application(app_name = appname, user_id = current_user.id, token=token, state='waiting approval')
        db.session.add(new_app)
        db.session.commit()
        return redirect(url_for('access.tokens'))

@access_app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('access.login'))