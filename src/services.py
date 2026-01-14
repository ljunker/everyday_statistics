from datetime import datetime, UTC, timedelta

from flask import g
from sqlalchemy import func

from src.db import db
from src.models import Event


def get_all_event_types():
    types = db.session.query(Event.type).filter_by(deleted=False).distinct().order_by(Event.type).all()
    return [t[0] for t in types]

def get_event_stats(event_type=None):
    query = Event.query.filter_by(deleted=False)
    if event_type:
        query = query.filter(Event.type == event_type)

    total_count = query.count()

    today = datetime.now(UTC).date()
    today_count = query.filter(
        func.date(Event.timestamp) == today
    ).count()

    year_start = datetime(today.year, 1, 1).date()
    year_count = query.filter(
        func.date(Event.timestamp) >= year_start
    ).count()

    first_event = db.session.query(func.min(Event.timestamp)).filter(Event.deleted == False)
    if event_type:
        first_event = first_event.filter(Event.type == event_type)
    first_event = first_event.scalar()

    if first_event:
        days_span = (today - first_event.date()).days + 1
        average_per_day = round(total_count / days_span, 2)
    else:
        average_per_day = 0

    distinct_dates_query = db.session.query(func.date(Event.timestamp)).filter(Event.deleted == False)
    if event_type:
        distinct_dates_query = distinct_dates_query.filter(Event.type == event_type)
    distinct_dates = distinct_dates_query.distinct().all()
    dates = []
    for d in distinct_dates:
        date_val = d[0]
        if isinstance(date_val, str):
            date_val = datetime.strptime(date_val, '%Y-%m-%d').date()
        dates.append(date_val)
    dates.sort()

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

    most_active_query = db.session.query(func.date(Event.timestamp), func.count()).filter(Event.deleted == False)
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

    hour_func = func.extract('hour', Event.timestamp)

    busiest_hour_query = (
        db.session.query(
            hour_func,
            func.count()
        )
        .filter(Event.deleted == False)
    )

    if event_type:
        busiest_hour_query = busiest_hour_query.filter(Event.type == event_type)

    busiest_hour = (
        busiest_hour_query
        .group_by(hour_func)
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
        'year_count': year_count,
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


def get_stats_t1_to_t2_for_user(type1, type2):
    # Get both types, ordered by timestamp
    events = Event.query.filter(
        Event.deleted == False,
        Event.type.in_([type1, type2])
    ).order_by(Event.timestamp).all()

    results = []
    last_type1 = None

    for event in events:
        if event.type == type1:
            last_type1 = event.timestamp
        elif event.type == type2 and last_type1:
            delta = event.timestamp - last_type1
            # Filter out huge or tiny deltas (optional)
            if timedelta(minutes=1) < delta < timedelta(hours=24):
                results.append(delta.total_seconds() / 60)
            last_type1 = None  # reset so only one type1 per type2

    if not results:
        return 0, -1, -1, -1

    avg_minutes = sum(results) / len(results)
    min_minutes = min(results)
    max_minutes = max(results)
    return len(results), avg_minutes, min_minutes, max_minutes
