'''
from flask import Flask, render_template, request, redirect, session, Blueprint
from .__init__ import db, login_manager


signup_app = Blueprint('signup_app', __name__, template_folder='../templates')


@signup_app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='GET': 
        return render_template('signup.html')
    else:
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first() 
        if user:
            flash('Username is not Available!')
            return redirect(url_for('access.signup'))
        new_user = User(username=user, name=name, \
                        password=generate_password_hash(password, \
                        method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('access.login'))
        '''