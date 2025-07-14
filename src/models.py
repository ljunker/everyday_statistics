from datetime import datetime, UTC

from src.db import db


class TypeMapping(db.Model):
    __tablename__ = 'type_mappings'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime(), default=datetime.now(UTC), index=True)
    deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    user_id = db.Column(db.String(50), nullable=False)
    quality = db.Column(db.Integer, nullable=True, index=True)
