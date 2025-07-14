from datetime import datetime

from pytz import UTC

from src.db import db
from src.models import Event


def test_stats(client, mocker):
    api_key = 'test_api_key'
    user_id = '281a1c09-aec7-4139-b6ad-e9a7aea7ea4c'

    func_mock = mocker.patch('src.cache.get_pocket_users')
    func_mock.return_value = [
        {
            "id": user_id,
            "username": "test",
            "email": "test@test.de",
            "firstName": "Test",
            "lastName": "Tester",
            "isAdmin": False,
            "locale": None,
            "customClaims": [{"key": "api-key", "value": api_key}],
            "userGroups": [],
            "ldapId": None,
            "disabled": False
        }
    ]

    event = Event(type='test_event', timestamp=datetime.fromisoformat(datetime.now(UTC).isoformat()), user_id=user_id, quality=None)

    db.session.add(event)
    db.session.commit()

    response = client.get(
        '/stats',
        headers={'X-API-KEY': api_key}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'total_count' in data[0]
