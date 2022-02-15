from functools import wraps
from flask import request

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'message': 'Authorization required to run this call'}, 401
        print('TOKEN: {}'.format(token))
        return f(*args, **kwargs)
    return decorated
