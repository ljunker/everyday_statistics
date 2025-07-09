from flask import Blueprint, request, session, redirect, url_for, render_template
from werkzeug.security import check_password_hash

from src.models import User

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            session['api_key'] = user.api_key
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@login_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login.login'))