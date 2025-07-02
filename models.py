from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC

from config import app

db = SQLAlchemy(app)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(UTC), index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    deleted = db.Column(db.Boolean, default=False, index=True)


class TypeMapping(db.Model):
    __tablename__ = 'type_mappings'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)

