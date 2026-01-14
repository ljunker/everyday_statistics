import os
from flask import session

def test_unauthenticated_redirect(client, monkeypatch):
    monkeypatch.setenv('APP_API_KEY', 'secret')
    # Dashboard should redirect to login
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_login_success(client, monkeypatch):
    api_key = 'secret'
    monkeypatch.setenv('APP_API_KEY', api_key)
    
    response = client.post('/login', data={'api_key': api_key}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Everyday Statistics Dashboard" in response.data
    
    # Check if session is set
    with client.session_transaction() as sess:
        assert sess['api_key'] == api_key

def test_login_failure(client, monkeypatch):
    monkeypatch.setenv('APP_API_KEY', 'secret')
    
    response = client.post('/login', data={'api_key': 'wrong'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid API Key" in response.data

def test_logout(client, monkeypatch):
    api_key = 'secret'
    monkeypatch.setenv('APP_API_KEY', api_key)
    
    # Login first
    client.post('/login', data={'api_key': api_key})
    
    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    
    # Check session is cleared
    with client.session_transaction() as sess:
        assert 'api_key' not in sess

def test_api_still_works_with_header(client, monkeypatch):
    api_key = 'secret'
    monkeypatch.setenv('APP_API_KEY', api_key)
    
    response = client.get('/events', headers={'X-API-KEY': api_key})
    assert response.status_code == 200

def test_api_fails_without_header(client, monkeypatch):
    monkeypatch.setenv('APP_API_KEY', 'secret')
    
    response = client.get('/events')
    assert response.status_code == 401

def test_decorators_abort_401(client, monkeypatch):
    # Test line 63 of decorators.py
    # This happens when login_required is called on an API-like path without session or API key
    monkeypatch.setenv('APP_API_KEY', 'secret')
    resp = client.get('/stats', follow_redirects=False)
    assert resp.status_code == 401

def test_prometheus_api_key_required(client, monkeypatch):
    monkeypatch.setenv('PROMETHEUS_API_KEY', 'prom_key')

    # Fail without header
    response = client.get('/metrics')
    assert response.status_code == 401

    # Fail with wrong key
    response = client.get('/metrics', headers={'X-API-KEY': 'wrong'})
    assert response.status_code == 401

    # Success with correct key
    response = client.get('/metrics', headers={'X-API-KEY': 'prom_key'})
    assert response.status_code == 200

def test_ui_routes(client, monkeypatch):
    monkeypatch.setenv('APP_API_KEY', 'secret')

    # Login first
    client.post('/login', data={'api_key': 'secret'})

    # Test dashboard
    response = client.get('/')
    assert response.status_code == 200
    assert b"Dashboard" in response.data

    # Test mappings UI
    response = client.get('/mapping')
    assert response.status_code == 200
    assert b"Type Mappings" in response.data

    # Test admin UI
    response = client.get('/admin')
    assert response.status_code == 200
    assert b"Admin Panel" in response.data
