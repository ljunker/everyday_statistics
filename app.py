import secrets

from flask import session, render_template
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from config import app
from decorators import login_required, admin_required
from models import (db, User)
from routes_admin import admin_bp
from routes_event import events_bp
from routes_login import login_bp

app.register_blueprint(events_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(login_bp)


@app.route('/')
@login_required
def dashboard():
    api_key = session['api_key']
    return render_template('index.html', api_key=api_key)


@app.route('/mappings-ui')
@login_required
def mappings_ui():
    api_key = session['api_key']
    return render_template('mappings.html', api_key=api_key)


@app.route('/admin')
@login_required  # use your session auth
@admin_required
def admin():
    api_key = session['api_key']
    return render_template('admin.html', api_key=api_key)


@app.cli.command('create-admin')
@with_appcontext
def create_admin():
    username = input('Admin username: ')
    password = input('Admin password: ')

    existing_admin = User.query.filter_by(username=username).first()
    if existing_admin:
        print(f"User {username} already exists.")
        return

    api_key = secrets.token_hex(32)
    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        api_key=api_key,
        is_admin=True
    )
    db.session.add(user)
    db.session.commit()
    print(f"✅ Created admin user {username}")
    print(f"🔑 API key: {api_key}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
