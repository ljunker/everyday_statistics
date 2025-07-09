from src.models import db, User


def test_create_event(client):
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

    response = client.post(
        '/events',
        json={'type': 'test_event'},
        headers={'X-API-KEY': api_key}
    )

    assert response.status_code == 201
    response = client.get(
        '/events',
        headers={'X-API-KEY': api_key}
    )
    data = response.get_json()
    assert len(data['events']) == 1
    assert data['events'][0]['type'] == 'test_event'