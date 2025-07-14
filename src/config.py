import os

from flask import Flask

from src.db import db
from src.logger import get_logger, init_logger
from src.routes.routes_admin import admin_bp
from src.routes.routes_event import events_bp
from src.scheduler import get_scheduler


def create_app(test_config=None):
    app = Flask(__name__)

    # ✅ Load default config from environment
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')

    app.config['SCHEDULER_API_ENABLED'] = True

    # ✅ Initialize the scheduler
    scheduler = get_scheduler()
    scheduler.init_app(app)
    scheduler.start()

    # ✅ Allow test overrides
    if test_config:
        app.config.update(test_config)

    # ✅ Initialize extensions
    db.init_app(app)

    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)

    # ✅ Set up logging
    init_logger(app.logger)

    return app
