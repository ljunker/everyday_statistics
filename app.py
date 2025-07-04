import secrets
from functools import wraps

from flask import Flask, request, jsonify, abort, session, redirect, url_for, render_template, g
from datetime import UTC
import os

from config import app
from models import (Event, TypeMapping, db, User)
from services import get_event_stats, get_all_stats


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            abort(401, description="Invalid or missing API key.")
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'current_user', None):
            abort(401, description="Authentication required.")
        if not g.current_user.is_admin:
            abort(403, description="Admin access required.")
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
@login_required
def dashboard():
    api_key = session['api_key']
    return render_template('index.html', api_key=api_key)


from werkzeug.security import check_password_hash
@app.route('/login', methods=['GET', 'POST'])
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
            return 'Invalid credentials', 401

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/mappings-ui')
@login_required
def mappings_ui():
    api_key = session['api_key']
    return render_template('mappings.html', api_key=api_key)


@app.route('/events', methods=['POST'])
@api_key_required
def create_event():
    data = request.get_json()
    event_type = data.get('type', 'unknown')
    latitude = data.get('latitude', 0.0)
    longitude = data.get('longitude', 0.0)
    timestamp = data.get('timestamp', datetime.now(UTC).isoformat())
    event = Event(type=event_type, latitude=latitude, longitude=longitude, timestamp=datetime.fromisoformat(timestamp))
    db.session.add(event)
    db.session.commit()
    return jsonify({'message': 'Event recorded!'}), 201


@app.route('/events', methods=['GET'])
@api_key_required
def get_events():
    event_type = request.args.get('type')

    query = Event.query
    if event_type:
        query = query.filter(Event.type == event_type)

    events = query.all()
    results = []
    for event in events:
        results.append({
            'id': event.id,
            'type': event.type,
            'timestamp': event.timestamp.isoformat(),
            'latitude': event.latitude,
            'longitude': event.longitude,
            'deleted': event.deleted
        })

    return jsonify({'events': results})


@app.route('/stats', methods=['GET'])
@api_key_required
def stats():
    event_type = request.args.get('type')
    if event_type:
        stats = get_event_stats(event_type)
    else:
        stats = get_all_stats()
    return jsonify(stats)


@app.route('/types', methods=['GET'])
@api_key_required
def get_event_types():
    types = db.session.query(Event.type).filter_by(deleted=False).distinct().all()
    type_list = [t[0] for t in types]
    return jsonify({
        'event_types': type_list
    })


@app.route('/events', methods=['DELETE'])
@api_key_required
def soft_delete_events_by_type():
    event_type = request.args.get('type')

    if not event_type:
        return jsonify({'error': 'Missing type parameter'}), 400

    updated_count = Event.query.filter_by(type=event_type, deleted=False) \
        .update({'deleted': True})
    db.session.commit()

    return jsonify({
        'message': f'Marked {updated_count} events of type \"{event_type}\" as deleted'
    }), 200


@app.route('/events/deleted', methods=['GET'])
@api_key_required
def get_deleted_events():
    deleted_events = Event.query.filter_by(deleted=True).all()

    results = []
    for event in deleted_events:
        results.append({
            'id': event.id,
            'type': event.type,
            'timestamp': event.timestamp.isoformat()
        })

    return jsonify({'deleted_events': results})


@app.route('/events/restore/<int:event_id>', methods=['POST'])
@api_key_required
def restore_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    if not event.deleted:
        return jsonify({'message': 'Event is already active'}), 400

    event.deleted = False
    db.session.commit()

    return jsonify({
        'message': f'Restored event {event_id}',
        'event': {
            'id': event.id,
            'type': event.type,
            'timestamp': event.timestamp.isoformat()
        }
    })


@app.route('/mappings', methods=['GET'])
@api_key_required
def list_mappings():
    mappings = TypeMapping.query.all()
    result = [{'id': m.id, 'type': m.type, 'display_name': m.display_name} for m in mappings]
    return jsonify(result)


@app.route('/mappings', methods=['POST'])
@api_key_required
def create_mapping():
    data = request.get_json()
    new_mapping = TypeMapping(type=data['type'], display_name=data['display_name'])
    db.session.add(new_mapping)
    db.session.commit()
    return jsonify({'message': 'Mapping created'})


@app.route('/mappings/<int:id>', methods=['PUT'])
@api_key_required
def update_mapping(id):
    mapping = TypeMapping.query.get(id)
    if not mapping:
        return jsonify({'error': 'Mapping not found'}), 404

    data = request.get_json()
    mapping.type = data.get('type', mapping.type)
    mapping.display_name = data.get('display_name', mapping.display_name)
    db.session.commit()
    return jsonify({'message': 'Mapping updated'})


@app.route('/mappings/<int:id>', methods=['DELETE'])
@api_key_required
def delete_mapping(id):
    mapping = TypeMapping.query.get(id)
    if not mapping:
        return jsonify({'error': 'Mapping not found'}), 404

    db.session.delete(mapping)
    db.session.commit()
    return jsonify({'message': 'Mapping deleted'})


from datetime import datetime, timedelta


@app.route('/timeline', methods=['GET'])
@api_key_required
def get_timeline():
    event_type = request.args.get('type')  # optional
    date_str = request.args.get('date')  # optional

    query = Event.query.filter_by(deleted=False)
    if event_type:
        query = query.filter(Event.type == event_type)

    if date_str:
        try:
            day = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

        # Get events for that day only
        start = datetime.combine(day, datetime.min.time())
        end = datetime.combine(day + timedelta(days=1), datetime.min.time())
        query = query.filter(Event.timestamp >= start, Event.timestamp < end)

    events = query.order_by(Event.timestamp.asc()).all()

    timeline = {}
    if date_str:
        timeline[date_str] = []
    for event in events:
        date = event.timestamp.strftime('%Y-%m-%d')
        time_str = event.timestamp.strftime('%H:%M')
        mapping = TypeMapping.query.filter_by(type=event.type).first()
        display_name = mapping.display_name if mapping else event.type
        timeline.setdefault(date, []).append({
            'id': event.id,
            'time': time_str,
            'type': event.type,
            'timestamp': event.timestamp.isoformat(),
            'display_name': display_name,
        })

    return jsonify({'timeline': timeline})


@app.route('/events/<int:event_id>', methods=['PUT'])
@api_key_required
def update_event(event_id):
    data = request.get_json()
    event = Event.query.get(event_id)
    if not event or event.deleted:
        return jsonify({'error': 'Event not found'}), 404

    event.type = data.get('type', event.type)
    new_ts = data.get('timestamp')
    if new_ts:
        try:
            event.timestamp = datetime.fromisoformat(new_ts)
        except ValueError:
            return jsonify({'error': 'Invalid timestamp format'}), 400

    db.session.commit()
    return jsonify({'message': 'Event updated'})


@app.route('/backup/export', methods=['GET'])
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
            'deleted': e.deleted
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


@app.route('/backup/import', methods=['POST'])
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
            deleted=e.get('deleted', False)
        ))

    db.session.bulk_save_objects(events)
    db.session.commit()

    return jsonify({'message': 'Database imported successfully'})


@app.route('/admin')
@login_required  # use your session auth
@admin_required
def admin():
    api_key = session['api_key']
    return render_template('admin.html', api_key=api_key)

from werkzeug.security import generate_password_hash

@app.route('/users', methods=['POST'])
@api_key_required
@admin_required
def create_user():
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


from flask.cli import with_appcontext

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
