def test_create_event(client, mocker):
    api_key = 'test_api_key'
    func_mock = mocker.patch('src.cache.get_pocket_users')
    func_mock.return_value = [
        {
            "id": "281a1c09-aec7-4139-b6ad-e9a7aea7ea4c",
            "username": "test",
            "email": "test@test.de",
            "firstName": "Test",
            "lastName": "Tester",
            "isAdmin": False,
            "locale": None,
            "customClaims":[{"key":"api-key","value":"test_api_key"}],
            "userGroups": [],
            "ldapId": None,
            "disabled": False
        }
    ]

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
