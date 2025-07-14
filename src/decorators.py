import os
from functools import wraps

import requests
from flask import request, abort, g, session

from src.cache import get_users_from_cache


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_key = request.headers.get('X-API-KEY')
        if not client_key:
            abort(401, description="Missing API key.")

        users = get_users_from_cache()
        matched_user = None

        for user in users:
            for claim in user.get("customClaims", []):
                if claim.get("key") == "api-key" and claim.get("value") == client_key:
                    matched_user = user
                    break
            if matched_user:
                break
        if not matched_user:
            abort(401, description="Invalid API key.")
        g.current_user = {
            'id': matched_user['id'],
            'username': matched_user['username'],
            'is_admin': matched_user.get('is_admin', False)
        }
        return f(*args, **kwargs)

    return decorated_function


def prometheus_api_key_required(f):
    prometheus_api_key = os.environ.get('PROMETHEUS_API_KEY')

    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        print(f"Received API key: {api_key}")  # Debugging line
        print(f"Expected Prometheus API key: {prometheus_api_key}")
        if not api_key or api_key != prometheus_api_key:
            abort(401, description="Invalid or missing special API key.")
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        remote_user = request.headers.get('remote_user', None)
        if not remote_user:
            abort(401, description="Not logged in.")
        users = get_users_from_cache()
        matched_user = None
        for user in users:
            if user.get('username') == remote_user:
                matched_user = user
                break
        if not matched_user:
            abort(401, description="User not found.")
        is_admin = False
        for group in matched_user.get("userGroups", []):
            if group.get("name") == "everyday_admin":
                is_admin = True
        if not is_admin:
            abort(403, description="Admin access required.")
        return f(*args, **kwargs)

    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        remote_user = request.headers.get('remote_user', None)
        if not remote_user:
            abort(401, description="Not logged in.")
        users = get_users_from_cache()
        matched_user = None
        for user in users:
            if user.get('username') == remote_user:
                matched_user = user
                break
        if not matched_user:
            abort(401, description="User not found.")
        session['api_key'] = None
        for claim in matched_user.get("customClaims", []):
            if claim.get("key") == "api-key":
                session['api_key'] = claim.get("value")
                break
        g.current_user = {
            'id': matched_user['id'],
            'username': matched_user['username'],
            'is_admin': matched_user.get('is_admin', False)
        }
        session['username'] = matched_user['firstName']
        return f(*args, **kwargs)

    return decorated_function
