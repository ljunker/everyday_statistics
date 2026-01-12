import secrets
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import text

from src.db import db
from src.decorators import admin_required, api_key_required
from src.models import Event, TypeMapping

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/backup/export', methods=['GET'])
@api_key_required
@admin_required
def export_db():
    events = Event.query.all()
    mappings = TypeMapping.query.all()

    events_data = [
        {
            'id': e.id,
            'type': e.type,
            'timestamp': e.timestamp.isoformat(),
            'deleted': e.deleted,
            'quality': e.quality
        }
        for e in events
    ]

    mappings_data = [
        {
            'id': m.id,
            'type': m.type,
            'display_name': m.display_name
        }
        for m in mappings
    ]

    return jsonify({
        'events': events_data,
        'mappings': mappings_data
    })


from werkzeug.security import generate_password_hash


@admin_bp.route('/backup/import', methods=['POST'])
@api_key_required
@admin_required
def import_db():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Clear existing data
    db.session.query(Event).delete()
    db.session.query(TypeMapping).delete()
    db.session.commit()

    # Re-insert mappings
    mappings = []
    for m in data.get('mappings', []):
        mappings.append(TypeMapping(
            id=m['id'],
            type=m['type'],
            display_name=m['display_name']
        ))

    db.session.bulk_save_objects(mappings)
    db.session.commit()

    # Re-insert events
    events = []
    for e in data.get('events', []):
        ts = datetime.fromisoformat(e['timestamp'])
        events.append(Event(
            id=e['id'],
            type=e['type'],
            timestamp=ts,
            deleted=e.get('deleted', False),
            quality=e.get('quality', None),
        ))

    db.session.bulk_save_objects(events)
    db.session.commit()

    return jsonify({'message': 'Database imported successfully'})


