from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC
import os

from sqlalchemy import func

app = Flask(__name__)

# Use environment variable for DB URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
API_KEY = os.getenv('API_KEY')


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(UTC), index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)


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


@app.route('/stats', methods=['GET'])
def get_stats():
    # Optional event type filter
    event_type = request.args.get('type')

    # Base query
    query = Event.query
    if event_type:
        query = query.filter(Event.type == event_type)

    # Total count
    total_count = query.count()

    # Today count
    today = datetime.now(UTC).date()
    today_count = query.filter(
        func.date(Event.timestamp) == today
    ).count()

    # Average per day
    first_event = db.session.query(func.min(Event.timestamp))
    if event_type:
        first_event = first_event.filter(Event.type == event_type)
    first_event = first_event.scalar()

    if first_event:
        days_span = (today - first_event.date()).days + 1
        average_per_day = round(total_count / days_span, 2)
    else:
        average_per_day = 0

    # Longest streak
    distinct_dates = (
        db.session.query(func.date(Event.timestamp))
        .filter(Event.type == event_type) if event_type else
        db.session.query(func.date(Event.timestamp))
    ).distinct().all()
    dates = sorted([d[0] for d in distinct_dates])

    longest_streak = 0
    current_streak = 0
    previous_date = None

    for date in dates:
        if previous_date and (date - previous_date).days == 1:
            current_streak += 1
        else:
            current_streak = 1
        longest_streak = max(longest_streak, current_streak)
        previous_date = date

    # Most active day
    most_active = (
        db.session.query(func.date(Event.timestamp), func.count())
        .filter(Event.type == event_type) if event_type else
        db.session.query(func.date(Event.timestamp), func.count())
    ).group_by(func.date(Event.timestamp)) \
     .order_by(func.count().desc()) \
     .first()

    if most_active:
        most_active_day = str(most_active[0])
        most_active_count = most_active[1]
    else:
        most_active_day = None
        most_active_count = 0

    # Poopiest hour
    most_active_hour = (
        db.session.query(func.extract('hour', Event.timestamp), func.count())
        .filter(Event.type == event_type) if event_type else
        db.session.query(func.extract('hour', Event.timestamp), func.count())
    ).group_by(func.extract('hour', Event.timestamp)) \
     .order_by(func.count().desc()) \
     .first()

    if most_active_hour:
        poopiest_hour_value = int(most_active_hour[0])
    else:
        poopiest_hour_value = None

    return jsonify({
        'type': event_type or 'all',
        'today_count': today_count,
        'total_count': total_count,
        'average_per_day': average_per_day,
        'longest_streak_days': longest_streak,
        'most_active_day': most_active_day,
        'most_active_day_count': most_active_count,
        'most_active_hour': poopiest_hour_value
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
