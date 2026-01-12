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
