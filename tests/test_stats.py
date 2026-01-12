from datetime import datetime

from pytz import UTC

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
    assert 'total_count' in data[0]

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
