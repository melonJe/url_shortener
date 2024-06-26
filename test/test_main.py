from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app

client = TestClient(app)


@patch('app.main.get_db')
@patch('app.service.url_service.create_short_url')
def test_create_short_url(mock_create_short_url, mock_get_db):
    mock_create_short_url.side_effect = ["short_key1", "short_key2", "short_key3", "short_key4", "short_key5", "short_key6"]
    mock_db = MagicMock(spec=Session)
    mock_get_db.return_value = mock_db

    # Test for same short_url for "http://www.example.com" and "www.example.com"
    response1 = client.post("/shorten", json={"url": "http://www.example.com", "expiry_days": 10})
    response2 = client.post("/shorten", json={"url": "www.example.com", "expiry_days": 10})
    assert response1.status_code == 200
    assert response2.status_code == 200

    # Test for different short_url for "www.example1.com" and "www.example2.com"
    response3 = client.post("/shorten", json={"url": "www.example1.com", "expiry_days": 10})
    response4 = client.post("/shorten", json={"url": "www.example2.com", "expiry_days": 10})
    assert response3.status_code == 200
    assert response4.status_code == 200

    # Test for expiry_days
    response5 = client.post("/shorten", json={"url": "http://example.com", "expiry_days": 10})
    response6 = client.post("/shorten", json={"url": "http://example.com"})
    assert response5.status_code == 200
    assert response6.status_code == 200


@patch('app.main.get_db')
@patch('app.service.url_service.get_original_url')
@patch('app.service.url_service.increment_access_count')
def test_get_original_url(mock_increment_access_count, mock_get_original_url, mock_get_db):
    mock_get_original_url.return_value = "http://example.com"
    mock_db = MagicMock(spec=Session)
    mock_get_db.return_value = mock_db

    response = client.get("/short_key")
    assert response.status_code == 200
    assert "http://example.com" in response.headers["location"]


@patch('app.main.get_db')
@patch('app.service.url_service.get_url_access_count')
def test_get_url_stats(mock_get_url_access_count, mock_get_db):
    mock_get_url_access_count.return_value = 5
    mock_db = MagicMock(spec=Session)
    mock_get_db.return_value = mock_db

    response = client.get("/stats/short_key")
    assert response.status_code == 200
    assert response.json() == {"count": 5}
