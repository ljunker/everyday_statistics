from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC

from config import app

db = SQLAlchemy(app)


class TypeMapping(db.Model):
    __tablename__ = 'type_mappings'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    api_key = db.Column(db.String(128), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(UTC), index=True)
    deleted = db.Column(db.Boolean, default=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.Relationship('User')