from flask import Blueprint, Response, render_template, session, redirect, url_for, request
import os
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge, generate_latest
from sqlalchemy import func

from src.db import db
from src.decorators import login_required, prometheus_api_key_required
from src.models import Event
from src.services import get_stats_t1_to_t2_for_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    api_key = session['api_key']
    username = session['username']
    return render_template('index.html', api_key=api_key, username=username)


@main_bp.route('/mapping')
@login_required
def mappings_ui():
    api_key = session['api_key']
    return render_template('mappings.html', api_key=api_key)


@main_bp.route('/admin')
@login_required
def admin():
    api_key = session['api_key']
    return render_template('admin.html', api_key=api_key)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        expected_key = os.environ.get('APP_API_KEY')
        if api_key == expected_key:
            session['api_key'] = api_key
            session['username'] = 'admin'
            return redirect(url_for('main.dashboard'))
        else:
            return render_template('login.html', error="Invalid API Key")
    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


EVENTS_TOTAL = Gauge('events_total', 'Total number of events recorded', ['type'])
COFFEE_TO_POOP_AVG = Gauge('coffee_to_poop_avg_minutes', 'Average time from coffee to poop in seconds')


@main_bp.route('/metrics')
@prometheus_api_key_required
def metrics():
    registry = CollectorRegistry()

    type_counts = db.session.query(Event.type, func.count()).filter(
        Event.deleted == False
    ).group_by(Event.type).all()

    for event_type, count in type_counts:
        EVENTS_TOTAL.labels(type=event_type).set(count)

    _, avg_minutes, _, _ = get_stats_t1_to_t2_for_user('coffee', 'poop')
    if avg_minutes != -1:
        COFFEE_TO_POOP_AVG.set(avg_minutes)

    registry.register(EVENTS_TOTAL)
    registry.register(COFFEE_TO_POOP_AVG)

    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)
