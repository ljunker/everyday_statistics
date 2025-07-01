from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Use environment variable for DB URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

@app.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    event_type = data.get('type', 'unknown')
    latitude = data.get('latitude', 0.0)
    longitude = data.get('longitude', 0.0)
    timestamp = data.get('timestamp', datetime.now().isoformat())
    event = Event(type=event_type, latitude=latitude, longitude=longitude, timestamp=datetime.fromisoformat(timestamp))
    db.session.add(event)
    db.session.commit()
    return jsonify({'message': 'Event recorded!'}), 201

@app.route('/stats', methods=['GET'])
def get_stats():
    today = datetime.utcnow().date()
    today_count = Event.query.filter(
        db.func.date(Event.timestamp) == today
    ).count()

    total_count = Event.query.count()

    return jsonify({
        'today_count': today_count,
        'total_count': total_count
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
