import secrets
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import text

from decorators import login_required, admin_required, api_key_required
from models import Event, TypeMapping, User, db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/backup/export', methods=['GET'])
@login_required
@admin_required
def export_db():
    events = Event.query.all()
    mappings = TypeMapping.query.all()
    users = User.query.all()

    users_data = [
        {
            'id': u.id,
            'username': u.username,
            'is_admin': u.is_admin,
            'api_key': u.api_key,
            'password_hash': u.password_hash  # Include password hash for context
        }
        for u in users
    ]

    events_data = [
        {
            'id': e.id,
            'type': e.type,
            'timestamp': e.timestamp.isoformat(),
            'deleted': e.deleted,
            'user_id': e.user_id,
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
        'users': users_data,
        'events': events_data,
        'mappings': mappings_data
    })


from werkzeug.security import generate_password_hash


@admin_bp.route('/backup/import', methods=['POST'])
@login_required
@admin_required
def import_db():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Clear existing data
    db.session.query(Event).delete()
    db.session.query(User).delete()
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

    # Re-insert users
    users = []
    for u in data.get('users', []):
        users.append(User(
            id=u['id'],
            username=u['username'],
            password_hash=generate_password_hash("changeme"),
            api_key=u['api_key'],
            is_admin=u.get('is_admin', False)
        ))
    db.session.bulk_save_objects(users)
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
            user_id=e['user_id'],
            quality=e.get('quality', None),
        ))

    db.session.bulk_save_objects(events)
    db.session.commit()

    db.session.execute(text("""
      SELECT setval('events_id_seq', (SELECT COALESCE(MAX(id), 1) FROM events));
      SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users));
      SELECT setval('type_mappings_id_seq', (SELECT COALESCE(MAX(id), 1) FROM type_mappings));
    """))
    db.session.commit()

    return jsonify({'message': 'Database imported successfully'})


@admin_bp.route('/users/<int:id>', methods=['DELETE'])
@api_key_required
@admin_required
def delete_user(id):
    user = User.query.get(id)
    if user and user.is_admin and g.current_user.id == id:
        return jsonify({'error': 'Cannot delete yourself as an admin'}), 403
    if not user:
        return jsonify({'error': 'Not found'}), 404
    events = Event.query.filter_by(user_id=id).all()
    if events:
        for event in events:
            db.session.delete(event)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})


@admin_bp.route('/users', methods=['POST', 'GET'])
@api_key_required
@admin_required
def create_user():
    if request.method == 'GET':
        users = User.query.all()
        user_list = [{'id': u.id, 'username': u.username, 'is_admin': u.is_admin, 'api_key': u.api_key} for u in users]
        return jsonify({'users': user_list})
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    api_key = secrets.token_hex(32)

    new_user = User(username=username,
                    password_hash=generate_password_hash(password),
                    is_admin=is_admin,
                    api_key=api_key
                    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'username': username, 'api_key': api_key, 'is_admin': is_admin})


@admin_bp.route('/users/<int:id>/password', methods=['PUT'])
@api_key_required
@admin_required
def update_user_password(id):
    data = request.get_json()
    new_password = data.get('password')

    if not new_password:
        return jsonify({'error': 'Password required'}), 400

    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message': f"Password updated for {user.username}."})


