from functools import wraps
from flask import abort, request, make_response, jsonify
from flask_login import current_user
import jwt
import os


def admin_required(f):
    @wraps(f)
    
    def decorated_function(*args, **kws):
        is_admin = getattr(current_user, 'idRol')
        if not (is_admin == 0):
            abort(401)
        return f(*args, **kws)
    return decorated_function

def gestor_required(f):
    @wraps(f)
    
    def decorated_function(*args, **kws):
        is_gestor = getattr(current_user, 'idRol')
        if not ((is_gestor == 1) or (is_gestor == 0)):
            abort(401)
        return f(*args, **kws)
    return decorated_function
