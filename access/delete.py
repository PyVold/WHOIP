import this
from flask import Flask, render_template, request, redirect, session, Blueprint, url_for, flash
from flask_login import UserMixin, login_user, logout_user, current_user, login_required, LoginManager
from . import access_app as deletes
from . import db, User, Application




@deletes.route('/delete/<int:app_id>')
@login_required
def delete_app(app_id):
    if app_id == 0:
        return redirect(url_for('access.tokens'))
    this_app = Application.query.filter_by(id = app_id).first()
    if this_app.user_id == current_user.id:
        db.session.delete(this_app)
        db.session.commit()
    return redirect(url_for('access.tokens'))
