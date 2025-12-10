import pytest
import json
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    """Create a Flask test client."""
    with app.test_client() as client:
        yield client

# ========== Tests for /api/v1/log_batch ==========

def test_log_batch_events_success(client):
    """Test logging a batch of events successfully."""
    mock_logs = [
        {"event": "click", "element": "button#buy-now"},
        {"event": "scroll", "depth": 90}
    ]
    with patch('db.insert_logs', return_value=True) as mock_insert:
        response = client.post('/api/v1/log_batch', json=mock_logs)
        data = json.loads(response.data)

        assert response.status_code == 201
        assert data['status'] == 'success'
        assert "Batch of 2 logs received" in data['message']
        mock_insert.assert_called_once()
        # Check that server_received_at was added
        assert all('server_received_at' in log for log in mock_insert.call_args[0][0])

def test_log_batch_events_invalid_payload(client):
    """Test logging with an invalid payload (not a list)."""
    response = client.post('/api/v1/log_batch', json={"data": "not a list"})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert "Invalid or empty batch" in data['message']

def test_log_batch_events_empty_list(client):
    """Test logging with an empty list."""
    response = client.post('/api/v1/log_batch', json=[])
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert "Invalid or empty batch" in data['message']

def test_log_batch_events_db_failure(client):
    """Test logging when the database insertion fails."""
    mock_logs = [{"event": "click", "element": "button#buy-now"}]
    with patch('db.insert_logs', return_value=False) as mock_insert:
        response = client.post('/api/v1/log_batch', json=mock_logs)
        data = json.loads(response.data)

        assert response.status_code == 500
        assert data['status'] == 'error'
        assert "Failed to save logs to database" in data['message']
        mock_insert.assert_called_once()

# ========== Tests for /api/v1/guide ==========

def test_get_guide_found(client):
    """Test getting a guide that exists."""
    mock_guide = {
        "_id": "60d5ecf3e5b7b6e4b8f2a4f7",
        "url": "https://example.com/pricing",
        "steps": [{"selector": "#btn-subscribe", "action": "click"}]
    }
    with patch('db.get_guide_for_url', return_value=mock_guide) as mock_get:
        response = client.get('/api/v1/guide?url=https://example.com/pricing')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['data']['url'] == mock_guide['url']
        assert str(data['data']['_id']) == mock_guide['_id'] # Check ID serialization
        mock_get.assert_called_once_with('https://example.com/pricing')

def test_get_guide_not_found(client):
    """Test getting a guide that does not exist."""
    with patch('db.get_guide_for_url', return_value=None) as mock_get:
        response = client.get('/api/v1/guide?url=https://example.com/unknown')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['data'] is None
        mock_get.assert_called_once_with('https://example.com/unknown')

def test_get_guide_no_url(client):
    """Test getting a guide without providing a URL parameter."""
    response = client.get('/api/v1/guide')
    data = json.loads(response.data)

    assert response.status_code == 400
    assert data['status'] == 'error'
    assert "URL parameter is required" in data['message']

