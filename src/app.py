from flask import session, render_template, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
from sqlalchemy import func

from src.cache import get_users_from_cache
from src.config import create_app
from src.db import db
from src.decorators import admin_required, prometheus_api_key_required, login_required
from src.models import Event
from src.services import get_stats_t1_to_t2_for_user

app = create_app()


@app.route('/')
@login_required
def dashboard():
    api_key = session['api_key']
    username = session['username']
    return render_template('index.html', api_key=api_key, username=username)


@app.route('/mappings-ui')
@login_required
def mappings_ui():
    api_key = session['api_key']
    return render_template('mappings.html', api_key=api_key)


@app.route('/admin')
@admin_required
def admin():
    api_key = session['api_key']
    return render_template('admin.html', api_key=api_key)


EVENTS_TOTAL = Gauge('events_total', 'Total number of events recorded', ['type', 'user_id'])
COFFEE_TO_POOP_AVG = Gauge('coffee_to_poop_avg_minutes', 'Average time from coffee to poop in seconds', ['user_id'])


@app.route('/metrics')
@prometheus_api_key_required
def metrics():
    registry = CollectorRegistry()
    users = get_users_from_cache()

    for user in users:
        type_counts = db.session.query(Event.type, func.count()).filter(
            Event.deleted == False,
            Event.user_id == user.id
        ).group_by(Event.type).all()

        for event_type, count in type_counts:
            EVENTS_TOTAL.labels(type=event_type, user_id=user.id).set(count)

        _, avg_minutes, _, _ = get_stats_t1_to_t2_for_user('coffee', 'poop', user.id)
        if avg_minutes != -1:
            COFFEE_TO_POOP_AVG.labels(user_id=user.id).set(avg_minutes)

    registry.register(EVENTS_TOTAL)
    registry.register(COFFEE_TO_POOP_AVG)

    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
