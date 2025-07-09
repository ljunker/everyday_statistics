import os
from flask import Flask

from src.db import db
from src.routes.routes_admin import admin_bp
from src.routes.routes_event import events_bp
from src.routes.routes_login import login_bp

def create_app(test_config=None):
    app = Flask(__name__)

    # ✅ Load default config from environment
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')

    # ✅ Allow test overrides
    if test_config:
        app.config.update(test_config)

    # ✅ Initialize extensions
    db.init_app(app)

    app.register_blueprint(events_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(admin_bp)

    return app
