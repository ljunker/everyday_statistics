def test_create_event(client):
    api_key = 'test_api_key'

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