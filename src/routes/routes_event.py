from flask import Blueprint, request, jsonify, g
from pytz import UTC

from src.db import db
from src.decorators import api_key_required
from src.models import Event, TypeMapping
from src.services import get_event_stats, get_all_stats, get_stats_t1_to_t2_for_user

events_bp = Blueprint('events', __name__)


@events_bp.route('/events', methods=['POST'])
@api_key_required
def create_event():
    data = request.get_json()
    event_type = data.get('type', 'unknown')
    timestamp = data.get('timestamp', datetime.now(UTC).isoformat())
    quality = data.get('quality', None)
    event = Event(type=event_type, timestamp=datetime.fromisoformat(timestamp), user_id=g.current_user['id'],
                  quality=quality)
    db.session.add(event)
    db.session.commit()
    return jsonify({'message': 'Event recorded!'}), 201


@events_bp.route('/events', methods=['GET'])
@api_key_required
def get_events():
    event_type = request.args.get('type')

    query = Event.query.filter_by(deleted=False, user_id=g.current_user['id'])
    if event_type:
        query = query.filter(Event.type == event_type)

    events = query.all()
    results = []
    for event in events:
        results.append({
            'id': event.id,
            'type': event.type,
            'timestamp': event.timestamp.isoformat(),
            'quality': event.quality,
            'deleted': event.deleted
        })

    return jsonify({'events': results})


@events_bp.route('/events', methods=['DELETE'])
@api_key_required
def soft_delete_events_by_type():
    event_type = request.args.get('type')

    if not event_type:
        return jsonify({'error': 'Missing type parameter'}), 400

    updated_count = Event.query.filter_by(type=event_type, deleted=False, user_id=g.current_user['id']) \
        .update({'deleted': True})
    db.session.commit()

    return jsonify({
        'message': f'Marked {updated_count} events of type \"{event_type}\" as deleted'
    }), 200


@events_bp.route('/events/<int:event_id>', methods=['DELETE'])
@api_key_required
def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    if event.deleted:
        return jsonify({'message': 'Event is already deleted'}), 400

    event.deleted = True
    db.session.commit()

    return jsonify({
        'message': f'Deleted event {event_id}',
        'event': {
            'id': event.id,
            'type': event.type,
            'timestamp': event.timestamp.isoformat()
        }
    })


@events_bp.route('/events/deleted', methods=['GET'])
@api_key_required
def get_deleted_events():
    deleted_events = Event.query.filter_by(deleted=True, user_id=g.current_user['id']).all()

    results = []
    for event in deleted_events:
        results.append({
            'id': event.id,
            'type': event.type,
            'timestamp': event.timestamp.isoformat()
        })

    return jsonify({'deleted_events': results})


@events_bp.route('/events/restore/<int:event_id>', methods=['POST'])
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


@events_bp.route('/events/<int:event_id>', methods=['PUT'])
@api_key_required
def update_event(event_id):
    data = request.get_json()
    event = Event.query.get(event_id)
    if not event or event.deleted:
        return jsonify({'error': 'Event not found'}), 404

    event.type = data.get('type', event.type)
    new_ts = data.get('timestamp')
    event.quality = data.get('quality', None)
    if new_ts:
        try:
            event.timestamp = datetime.fromisoformat(new_ts)
        except ValueError:
            return jsonify({'error': 'Invalid timestamp format'}), 400

    db.session.commit()
    return jsonify({'message': 'Event updated'})


@events_bp.route('/stats', methods=['GET'])
@api_key_required
def stats():
    event_type = request.args.get('type')
    if event_type:
        stats = get_event_stats(event_type)
    else:
        stats = get_all_stats()
    return jsonify(stats)


@events_bp.route('/types', methods=['GET'])
@api_key_required
def get_event_types():
    types = db.session.query(Event.type).filter_by(deleted=False, user_id=g.current_user['id']).distinct().all()
    type_list = [t[0] for t in types]
    return jsonify({
        'event_types': type_list
    })


@events_bp.route('/mappings', methods=['GET'])
@api_key_required
def list_mappings():
    mappings = TypeMapping.query.all()
    result = [{'id': m.id, 'type': m.type, 'display_name': m.display_name} for m in mappings]
    return jsonify(result)


@events_bp.route('/mappings', methods=['POST'])
@api_key_required
def create_mapping():
    data = request.get_json()
    new_mapping = TypeMapping(type=data['type'], display_name=data['display_name'])
    db.session.add(new_mapping)
    db.session.commit()
    return jsonify({'message': 'Mapping created'})


@events_bp.route('/mappings/<int:id>', methods=['PUT'])
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


@events_bp.route('/mappings/<int:id>', methods=['DELETE'])
@api_key_required
def delete_mapping(id):
    mapping = TypeMapping.query.get(id)
    if not mapping:
        return jsonify({'error': 'Mapping not found'}), 404

    db.session.delete(mapping)
    db.session.commit()
    return jsonify({'message': 'Mapping deleted'})


from datetime import datetime, timedelta


@events_bp.route('/timeline', methods=['GET'])
@api_key_required
def get_timeline():
    event_type = request.args.get('type')  # optional
    date_str = request.args.get('date')  # optional

    query = Event.query.filter_by(deleted=False, user_id=g.current_user['id'])
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
            'quality': event.quality,
            'display_name': display_name,
        })

    return jsonify({'timeline': timeline})


@events_bp.route('/stats/<type1>_to_<type2>', methods=['GET'])
@api_key_required
def generic_time_gap(type1, type2):
    user_id = g.current_user['id']

    mapping_type1 = TypeMapping.query.filter_by(type=type1).first()
    mapping_type2 = TypeMapping.query.filter_by(type=type2).first()

    results_length, avg_minutes, min_minutes, max_minutes = get_stats_t1_to_t2_for_user(type1, type2, user_id)

    return jsonify({
        'type1': type1,
        'mapping_type1': mapping_type1.display_name if mapping_type1 else type1,
        'type2': type2,
        'mapping_type2': mapping_type2.display_name if mapping_type2 else type2,
        'count': results_length,
        'average_minutes': round(avg_minutes, 2),
        'min_minutes': round(min_minutes, 2),
        'max_minutes': round(max_minutes, 2)
    })
