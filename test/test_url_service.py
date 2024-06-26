from unittest.mock import patch, MagicMock

from sqlalchemy.orm import Session

from app.service.url_service import create_short_url, get_original_url, increment_access_count, get_url_access_count


@patch('app.service.url_service.redis_client')
def test_create_short_url(mock_redis_client):
    db = MagicMock(spec=Session)
    mock_redis_client.get.return_value = None
    db.query.return_value.filter.return_value.first.return_value = None

    # Test for same short_url for "http://www.example.com" and "www.example.com"
    short_key1 = create_short_url(db, "http://www.example.com", 10)
    short_key2 = create_short_url(db, "www.example.com", 10)
    assert short_key1 == short_key2

    # Test for different short_url for "www.example1.com" and "www.example2.com"
    short_key3 = create_short_url(db, "www.example1.com", 10)
    short_key4 = create_short_url(db, "www.example2.com", 10)
    assert short_key3 != short_key4

    db.add.assert_called()
    db.commit.assert_called()


@patch('app.service.url_service.redis_client')
def test_get_original_url(mock_redis_client):
    db = MagicMock(spec=Session)
    mock_redis_client.get.return_value = "http://example.com"

    url = get_original_url(db, "short_key")
    assert url == "http://example.com"


@patch('app.service.url_service.redis_client')
def test_increment_access_count(mock_redis_client):
    increment_access_count("short_key")
    mock_redis_client.incr.assert_called_once_with("count:short_key")


@patch('app.service.url_service.redis_client')
def test_get_url_access_count(mock_redis_client):
    db = MagicMock(spec=Session)
    mock_redis_client.get.return_value = 5

    count = get_url_access_count(db, "short_key")
    assert count == 5
