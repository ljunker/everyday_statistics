def test_create_event(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

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

def test_delete_and_restore_event(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    # Create event
    client.post('/events', json={'type': 'test_event'}, headers={'X-API-KEY': api_key})
    event_id = client.get('/events', headers={'X-API-KEY': api_key}).get_json()['events'][0]['id']

    # Delete event
    response = client.delete(f'/events/{event_id}', headers={'X-API-KEY': api_key})
    assert response.status_code == 200
    
    # Verify it's not in active events
    response = client.get('/events', headers={'X-API-KEY': api_key})
    assert len(response.get_json()['events']) == 0

    # Verify it is in deleted events
    response = client.get('/events/deleted', headers={'X-API-KEY': api_key})
    assert len(response.get_json()['deleted_events']) == 1

    # Restore event
    response = client.post(f'/events/restore/{event_id}', headers={'X-API-KEY': api_key})
    assert response.status_code == 200

    # Verify it's active again
    response = client.get('/events', headers={'X-API-KEY': api_key})
    assert len(response.get_json()['events']) == 1

def test_update_event(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    # Create event
    client.post('/events', json={'type': 'old_type'}, headers={'X-API-KEY': api_key})
    event_id = client.get('/events', headers={'X-API-KEY': api_key}).get_json()['events'][0]['id']

    # Update event
    response = client.put(
        f'/events/{event_id}',
        json={'type': 'new_type', 'quality': 9},
        headers={'X-API-KEY': api_key}
    )
    assert response.status_code == 200

    # Verify update
    response = client.get('/events', headers={'X-API-KEY': api_key})
    event = response.get_json()['events'][0]
    assert event['type'] == 'new_type'
    assert event['quality'] == 9

def test_get_timeline(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    from datetime import datetime, UTC
    now = datetime.now(UTC)
    date_str = now.strftime('%Y-%m-%d')

    client.post('/events', json={'type': 'coffee', 'timestamp': now.isoformat()}, headers={'X-API-KEY': api_key})

    response = client.get(f'/timeline?date={date_str}', headers={'X-API-KEY': api_key})
    assert response.status_code == 200
    data = response.get_json()
    assert date_str in data['timeline']
    assert len(data['timeline'][date_str]) == 1
    assert data['timeline'][date_str][0]['type'] == 'coffee'
