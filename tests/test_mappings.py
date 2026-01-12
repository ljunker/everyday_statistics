def test_list_mappings(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    response = client.get('/mappings', headers={'X-API-KEY': api_key})
    assert response.status_code == 200
    assert response.get_json() == []

def test_create_mapping(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    response = client.post(
        '/mappings',
        json={'type': 'coffee', 'display_name': 'I drank a coffee'},
        headers={'X-API-KEY': api_key}
    )
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Mapping created'

    response = client.get('/mappings', headers={'X-API-KEY': api_key})
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['type'] == 'coffee'
    assert data[0]['display_name'] == 'I drank a coffee'

def test_update_mapping(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    # First create
    client.post(
        '/mappings',
        json={'type': 'coffee', 'display_name': 'I drank a coffee'},
        headers={'X-API-KEY': api_key}
    )
    
    mapping_id = client.get('/mappings', headers={'X-API-KEY': api_key}).get_json()[0]['id']

    response = client.put(
        f'/mappings/{mapping_id}',
        json={'display_name': 'Super Coffee'},
        headers={'X-API-KEY': api_key}
    )
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Mapping updated'

    response = client.get('/mappings', headers={'X-API-KEY': api_key})
    assert response.get_json()[0]['display_name'] == 'Super Coffee'

def test_delete_mapping(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    # First create
    client.post(
        '/mappings',
        json={'type': 'coffee', 'display_name': 'I drank a coffee'},
        headers={'X-API-KEY': api_key}
    )
    
    mapping_id = client.get('/mappings', headers={'X-API-KEY': api_key}).get_json()[0]['id']

    response = client.delete(f'/mappings/{mapping_id}', headers={'X-API-KEY': api_key})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Mapping deleted'

    response = client.get('/mappings', headers={'X-API-KEY': api_key})
    assert response.get_json() == []
