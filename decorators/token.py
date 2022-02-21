from functools import wraps
from flask import request
from flask_login import current_user
from access import User, Application, db

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
            tokencheck = Application.lookup(token=token)
            if not tokencheck:
                return {'message': 'Token is not recognized'}, 401
            if tokencheck.state != 'active':
                return {'message': 'Token is either disabled or need approval!'}, 401
            tokencheck.calls_count += 1
            db.session.commit()
        if not token:
            return {'message': 'Authorization required to run this call: go to https://ipdevops.com/myapi/tokens'}, 401

        return f(*args, **kwargs)
    return decorated
