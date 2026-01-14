from datetime import datetime, UTC, timedelta
from src.db import db
from src.models import Event

def test_stats(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    event = Event(type='test_event', timestamp=datetime.fromisoformat(datetime.now(UTC).isoformat()), quality=None)

    db.session.add(event)
    db.session.commit()

    response = client.get(
        '/stats',
        headers={'X-API-KEY': api_key}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'year_count' in data

def test_stats_per_type(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    db.session.add(Event(type='type_a', timestamp=datetime.now(UTC)))
    db.session.add(Event(type='type_b', timestamp=datetime.now(UTC)))
    db.session.commit()

    response = client.get(
        '/stats/types',
        headers={'X-API-KEY': api_key}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    types = [s['type'] for s in data]
    assert 'type_a' in types
    assert 'type_b' in types
    for entry in data:
        assert 'year_count' in entry

def test_year_stats(app):
    from src.services import get_event_stats
    from src.models import Event
    from src.db import db
    from datetime import datetime, UTC, timedelta

    with app.app_context():
        now = datetime.now(UTC)
        # Event from this year
        db.session.add(Event(type='year_test', timestamp=now))
        # Event from last year
        last_year = now.replace(year=now.year - 1)
        db.session.add(Event(type='year_test', timestamp=last_year))
        db.session.commit()

        stats = get_event_stats('year_test')
        assert stats['total_count'] == 2
        assert stats['year_count'] == 1

def test_service_edge_cases(app):
    from src.services import get_event_stats
    from src.models import Event
    from src.db import db
    from datetime import datetime, UTC, timedelta

    with app.app_context():
        # Case 1: No events at all
        stats = get_event_stats()
        assert stats['total_count'] == 0
        assert stats['average_per_day'] == 0

        # Case 2: Streak and Most active
        now = datetime.now(UTC)
        # Day 1
        db.session.add(Event(type='streak', timestamp=now - timedelta(days=2)))
        # Day 2 (gap)
        # Day 3
        db.session.add(Event(type='streak', timestamp=now))
        db.session.add(Event(type='streak', timestamp=now)) # Two on same day
        db.session.commit()

        stats = get_event_stats('streak')
        assert stats['total_count'] == 3
        assert stats['longest_streak_days'] == 1
        assert stats['most_active_day_count'] == 2

def test_routes_main_metrics(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('PROMETHEUS_API_KEY', api_key)
    
    # Add coffee and poop events for gap stat coverage in metrics
    now = datetime.now(UTC)
    db.session.add(Event(type='coffee', timestamp=now - timedelta(minutes=30)))
    db.session.add(Event(type='poop', timestamp=now))
    db.session.commit()
    
    # Metrics endpoint requires prometheus_api_key_required
    resp = client.get('/metrics', headers={'X-API-KEY': api_key})
    assert resp.status_code == 200
    content = resp.data.decode('utf-8')
    assert 'events_total{type="coffee"} 1.0' in content
    assert 'coffee_to_poop_avg_minutes 30.0' in content

def test_services_streak_increment(app):
    from src.services import get_event_stats
    with app.app_context():
        now = datetime.now(UTC).date()
        # Day 1
        db.session.add(Event(type='streak_test', timestamp=datetime.combine(now - timedelta(days=1), datetime.min.time())))
        # Day 2
        db.session.add(Event(type='streak_test', timestamp=datetime.combine(now, datetime.min.time())))
        db.session.commit()
        
        stats = get_event_stats('streak_test')
        assert stats['longest_streak_days'] == 2
