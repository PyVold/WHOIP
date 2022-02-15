from flask import Flask, render_template, request, redirect, session, Blueprint, url_for
from flask_login import UserMixin, login_user, logout_user, current_user, login_required, LoginManager
from urllib.parse import urlparse, urljoin
from . import auth_app as access_app
from . import db


login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True)

    def __repr__(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@access_app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return render_template('login.html', message = 'User not found')
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
    


@access_app.route('/tokens/', methods=['GET', 'POST'])
@login_required
def tokens():
    return render_template('tokens.html')

@access_app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('access.login'))