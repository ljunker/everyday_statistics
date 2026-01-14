from datetime import datetime, UTC
from src.models import Event
from src.db import db

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

def test_event_errors(client, monkeypatch):
    api_key = 'secret'
    monkeypatch.setenv('APP_API_KEY', api_key)

    # 1. Soft delete by type - missing type parameter
    response = client.delete('/events', headers={'X-API-KEY': api_key})
    assert response.status_code == 400
    assert b"Missing type parameter" in response.data

    # 2. Delete single event - not found
    response = client.delete('/events/9999', headers={'X-API-KEY': api_key})
    assert response.status_code == 404

    # 3. Delete single event - already deleted
    client.post('/events', json={'type': 'test'}, headers={'X-API-KEY': api_key})
    event_id = client.get('/events', headers={'X-API-KEY': api_key}).get_json()['events'][0]['id']
    client.delete(f'/events/{event_id}', headers={'X-API-KEY': api_key})
    response = client.delete(f'/events/{event_id}', headers={'X-API-KEY': api_key})
    assert response.status_code == 400
    assert b"already deleted" in response.data

    # 4. Restore event - not found
    response = client.post('/events/restore/9999', headers={'X-API-KEY': api_key})
    assert response.status_code == 404

    # 5. Restore event - already active
    client.post('/events', json={'type': 'active'}, headers={'X-API-KEY': api_key})
    events = client.get('/events', headers={'X-API-KEY': api_key}).get_json()['events']
    active_id = next(e['id'] for e in events if e['type'] == 'active')
    response = client.post(f'/events/restore/{active_id}', headers={'X-API-KEY': api_key})
    assert response.status_code == 400
    assert b"already active" in response.data

    # 6. Update event - invalid timestamp
    response = client.put(f'/events/{active_id}', json={'timestamp': 'invalid'}, headers={'X-API-KEY': api_key})
    assert response.status_code == 400
    assert b"Invalid timestamp format" in response.data

    # 7. Update event - not found
    response = client.put('/events/9999', json={'type': 'new'}, headers={'X-API-KEY': api_key})
    assert response.status_code == 404

    # 8. Timeline - invalid date
    response = client.get('/timeline?date=not-a-date', headers={'X-API-KEY': api_key})
    assert response.status_code == 400

def test_routes_event_more_coverage(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    # 1. Test filtering events by type in get_events
    db.session.add(Event(type='type1', timestamp=datetime.now(UTC)))
    db.session.add(Event(type='type2', timestamp=datetime.now(UTC)))
    db.session.commit()

    resp = client.get('/events?type=type1', headers={'X-API-KEY': api_key})
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['events']) == 1
    assert data['events'][0]['type'] == 'type1'

    # 2. Test soft_delete_events_by_type
    resp = client.delete('/events?type=type1', headers={'X-API-KEY': api_key})
    assert resp.status_code == 200
    assert 'Marked 1 events' in resp.get_json()['message']

    # 3. Test get_event_types
    resp = client.get('/types', headers={'X-API-KEY': api_key})
    assert resp.status_code == 200
    assert 'type2' in resp.get_json()['event_types']
    assert 'type1' not in resp.get_json()['event_types'] # because it's deleted

    # 4. Test timeline filtering by type
    now = datetime.now(UTC)
    date_str = now.strftime('%Y-%m-%d')
    db.session.add(Event(type='timeline_type', timestamp=now))
    db.session.commit()

    resp = client.get(f'/timeline?date={date_str}&type=timeline_type', headers={'X-API-KEY': api_key})
    assert resp.status_code == 200
    assert date_str in resp.get_json()['timeline']
    assert len(resp.get_json()['timeline'][date_str]) == 1

    # 5. Test stats with type
    resp = client.get('/stats?type=type2', headers={'X-API-KEY': api_key})
    assert resp.status_code == 200
    assert resp.get_json()['type'] == 'type2'
