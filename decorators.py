from functools import wraps

from flask import request, abort, g, session, redirect, url_for

from models import User


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            abort(401, description="Invalid or missing API key.")
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            abort(401, description="Authentication required.")
        if not session.get('is_admin'):
            abort(403, description="Admin access required.")
        return f(*args, **kwargs)

    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)

    return decorated_function