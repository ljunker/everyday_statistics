from datetime import datetime, timedelta, UTC

def test_generic_time_gap(client, monkeypatch):
    api_key = 'test_api_key'
    monkeypatch.setenv('APP_API_KEY', api_key)

    base_time = datetime.now(UTC)
    
    # Event 1: coffee at T
    client.post('/events', json={
        'type': 'coffee',
        'timestamp': base_time.isoformat()
    }, headers={'X-API-KEY': api_key})

    # Event 2: work at T + 30 mins
    client.post('/events', json={
        'type': 'work',
        'timestamp': (base_time + timedelta(minutes=30)).isoformat()
    }, headers={'X-API-KEY': api_key})

    # Event 3: coffee at T + 2 hours
    client.post('/events', json={
        'type': 'coffee',
        'timestamp': (base_time + timedelta(hours=2)).isoformat()
    }, headers={'X-API-KEY': api_key})

    # Event 4: work at T + 2 hours 45 mins
    client.post('/events', json={
        'type': 'work',
        'timestamp': (base_time + timedelta(hours=2, minutes=45)).isoformat()
    }, headers={'X-API-KEY': api_key})

    response = client.get('/stats/coffee_to_work', headers={'X-API-KEY': api_key})
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['type1'] == 'coffee'
    assert data['type2'] == 'work'
    assert data['count'] == 2
    # (30 + 45) / 2 = 37.5
    assert data['average_minutes'] == 37.5
    assert data['min_minutes'] == 30.0
    assert data['max_minutes'] == 45.0
