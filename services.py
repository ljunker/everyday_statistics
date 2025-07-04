from datetime import datetime, UTC

from flask import g
from sqlalchemy import func

from models import Event, db


def get_all_event_types():
    types = db.session.query(Event.type).filter_by(deleted=False, user_id=g.current_user.id).distinct().order_by(Event.type).all()
    return [t[0] for t in types]

def get_event_stats(event_type=None):
    query = Event.query.filter_by(deleted=False, user_id=g.current_user.id)
    if event_type:
        query = query.filter(Event.type == event_type)

    total_count = query.count()

    today = datetime.now(UTC).date()
    today_count = query.filter(
        func.date(Event.timestamp) == today
    ).count()

    first_event = db.session.query(func.min(Event.timestamp)).filter(Event.deleted == False, Event.user_id == g.current_user.id)
    if event_type:
        first_event = first_event.filter(Event.type == event_type)
    first_event = first_event.scalar()

    if first_event:
        days_span = (today - first_event.date()).days + 1
        average_per_day = round(total_count / days_span, 2)
    else:
        average_per_day = 0

    distinct_dates_query = db.session.query(func.date(Event.timestamp)).filter(Event.deleted == False, Event.user_id == g.current_user.id)
    if event_type:
        distinct_dates_query = distinct_dates_query.filter(Event.type == event_type)
    distinct_dates = distinct_dates_query.distinct().all()
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

    most_active_query = db.session.query(func.date(Event.timestamp), func.count()).filter(Event.deleted == False, Event.user_id == g.current_user.id)
    if event_type:
        most_active_query = most_active_query.filter(Event.type == event_type)
    most_active = (
        most_active_query.group_by(func.date(Event.timestamp))
        .order_by(func.count().desc())
        .first()
    )

    if most_active:
        most_active_day = str(most_active[0])
        most_active_count = most_active[1]
    else:
        most_active_day = None
        most_active_count = 0

    busiest_hour_query = db.session.query(
        func.extract(
            'hour',
            Event.timestamp.op('AT TIME ZONE')('Europe/Berlin')
        ),
        func.count()
    ).filter(Event.deleted == False, Event.user_id == g.current_user.id)
    if event_type:
        busiest_hour_query = busiest_hour_query.filter(Event.type == event_type)
    busiest_hour = (
        busiest_hour_query.group_by(func.extract('hour', Event.timestamp.op('AT TIME ZONE')('Europe/Berlin')))
        .order_by(func.count().desc())
        .first()
    )

    if busiest_hour:
        busiest_hour_value = int(busiest_hour[0])
    else:
        busiest_hour_value = None

    return {
        'type': event_type or 'all',
        'today_count': today_count,
        'total_count': total_count,
        'average_per_day': average_per_day,
        'longest_streak_days': longest_streak,
        'most_active_day': most_active_day,
        'most_active_day_count': most_active_count,
        'most_active_hour': busiest_hour_value
    }

def get_all_stats():
    all_types = get_all_event_types()
    stats = []
    for t in all_types:
        stats.append(get_event_stats(t))
    return stats
