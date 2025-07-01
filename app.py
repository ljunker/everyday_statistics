from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC
import os

from sqlalchemy import func

from config import app
from models import Event, db
from services import get_event_stats, get_all_stats

API_KEY = os.getenv('API_KEY')


@app.before_request
def check_api_key():
    if request.endpoint == 'index':
        return  # if you have a root/index route that needs to be public
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        abort(401, description="Invalid or missing API key.")


@app.route('/')
def index():
    return "Everyday Statistics Service"


@app.route('/events', methods=['POST'])
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
def stats():
    event_type = request.args.get('type')
    if event_type:
        stats = get_event_stats(event_type)
    else:
        stats = get_all_stats()
    return jsonify(stats)


@app.route('/types', methods=['GET'])
def get_event_types():
    types = db.session.query(Event.type).filter_by(deleted=False).distinct().all()
    type_list = [t[0] for t in types]
    return jsonify({
        'event_types': type_list
    })


@app.route('/events', methods=['DELETE'])
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



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
