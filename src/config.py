import os

from flask import Flask

from src.db import db
from src.logger import init_logger
from src.routes.routes_admin import admin_bp
from src.routes.routes_event import events_bp
from src.routes.routes_main import main_bp
from src.scheduler import get_scheduler


def create_app(test_config=None):
    app = Flask(__name__)

    # ✅ Load default config from environment
    default_db = 'sqlite:///instance/stats.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', default_db)
    if test_config is not None and test_config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = test_config['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure instance folder exists
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        # Handle relative paths by making them absolute relative to the app root
        if not os.path.isabs(db_path):
            # We assume the app root is one level up from this file (src/config.py)
            app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.abspath(os.path.join(app_root, db_path))
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
        
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')

    app.config['SCHEDULER_API_ENABLED'] = True

    # ✅ Initialize the scheduler
    scheduler = get_scheduler()
    if test_config and not test_config.get('TESTING', True):
        scheduler.init_app(app)
        scheduler.start()

    # ✅ Allow test overrides
    if test_config:
        # Don't overwrite SQLALCHEMY_DATABASE_URI if we already resolved it to absolute
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        app.config.update(test_config)
        if db_uri and db_uri.startswith('sqlite:////'):
             app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    # ✅ Initialize extensions
    db.init_app(app)

    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    # ✅ Set up logging
    init_logger(app.logger)

    return app
