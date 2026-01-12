import json

def test_export_db(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    # Create an event and a mapping to export
    client.post('/events', json={'type': 'test_event'}, headers={'X-API-KEY': api_key})
    client.post('/mappings', json={'type': 'test_event', 'display_name': 'Test Event'}, headers={'X-API-KEY': api_key})

    response = client.get('/backup/export', headers={'X-API-KEY': api_key})
    assert response.status_code == 200
    data = response.get_json()
    assert 'events' in data
    assert 'mappings' in data
    assert len(data['events']) == 1
    assert len(data['mappings']) == 1
    assert data['events'][0]['type'] == 'test_event'
    assert data['mappings'][0]['type'] == 'test_event'

def test_import_db(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    backup_data = {
        'events': [
            {
                'id': 1,
                'type': 'imported_event',
                'timestamp': '2026-01-12T10:00:00Z',
                'deleted': False,
                'quality': 5
            }
        ],
        'mappings': [
            {
                'id': 1,
                'type': 'imported_event',
                'display_name': 'Imported Event'
            }
        ]
    }

    response = client.post(
        '/backup/import',
        json=backup_data,
        headers={'X-API-KEY': api_key}
    )
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Database imported successfully'

    # Verify import
    response = client.get('/events', headers={'X-API-KEY': api_key})
    data = response.get_json()
    assert len(data['events']) == 1
    assert data['events'][0]['type'] == 'imported_event'

    response = client.get('/mappings', headers={'X-API-KEY': api_key})
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['type'] == 'imported_event'

def test_admin_import_invalid(client, monkeypatch):
    api_key = 'secret'
    monkeypatch.setenv('APP_API_KEY', api_key)
    # Use Content-Type: application/json but empty body to trigger 400 in our code
    response = client.post('/backup/import', data='null', content_type='application/json', headers={'X-API-KEY': api_key})
    assert response.status_code == 400
