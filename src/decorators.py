import os
from functools import wraps

from flask import request, abort, g, session, redirect, url_for


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        expected_key = os.environ.get('APP_API_KEY', 'supersecretapikey')
        client_key = request.headers.get('X-API-KEY')
        if not client_key or client_key != expected_key:
            abort(401, description="Invalid or missing API key.")

        g.current_user = {
            'id': 'default_user',
            'username': 'admin',
            'is_admin': True
        }
        return f(*args, **kwargs)

    return decorated_function


def prometheus_api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        prometheus_api_key = os.environ.get('PROMETHEUS_API_KEY')
        api_key = request.headers.get('X-API-KEY')
        if not api_key or api_key != prometheus_api_key:
            abort(401, description="Invalid or missing special API key.")
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Since it's single user, we just check API key via api_key_required
        return f(*args, **kwargs)

    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a single-user system without "complicated auth", 
        # we can assume the user is "logged in" if they have the API key or if we are in a session.
        # But if the user wants "just the api key", maybe we should check the API key here too,
        # or just rely on a simple check.
        
        expected_key = os.environ.get('APP_API_KEY', 'supersecretapikey')
        client_key = request.headers.get('X-API-KEY') or session.get('api_key')
        
        if not client_key or client_key != expected_key:
            if request.path.startswith('/events') or \
               request.path.startswith('/stats') or \
               request.path.startswith('/types') or \
               request.path.startswith('/mappings') or \
               request.path.startswith('/backup'):
                abort(401, description="Invalid or missing API key.")
            return redirect(url_for('main.login'))
            
        session['api_key'] = client_key
        session['username'] = 'admin'
        g.current_user = {
            'id': 'default_user',
            'username': 'admin',
            'is_admin': True
        }
        return f(*args, **kwargs)

    return decorated_function
