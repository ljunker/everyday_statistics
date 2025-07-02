from functools import wraps

from flask import Flask, request, jsonify, abort, session, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC
import os

from sqlalchemy import func

from config import app
from models import Event, db
from services import get_event_stats, get_all_stats

API_KEY = os.getenv('API_KEY')


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key != API_KEY:
            abort(401, description="Invalid or missing API key.")
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
    api_key = os.getenv('API_KEY')
    return render_template('index.html', api_key=api_key)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == os.getenv('LOGIN_USER') and password == os.getenv('LOGIN_PASS'):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials', 401

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


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
        timeline.setdefault(date, []).append({
            'time': time_str,
            'type': event.type
        })

    return jsonify({'timeline': timeline})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
