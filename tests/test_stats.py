from datetime import datetime

from pytz import UTC

from src.db import db
from src.models import User, Event


def test_stats(client):
    api_key = 'test_api_key'

    # insert test user with the api_key
    user = User(
        username="tester",
        password_hash="1234",
        api_key=api_key,
        is_admin=False
    )

    db.session.add(user)
    db.session.commit()

    user_id = User.query.first().id

    event = Event(type='test_event', timestamp=datetime.fromisoformat(datetime.now(UTC).isoformat()), user_id=user_id, quality=None)

    db.session.add(event)
    db.session.commit()

    response = client.get(
        '/stats',
        headers={'X-API-KEY': api_key}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'total_count' in data
