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
