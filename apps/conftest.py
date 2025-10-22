# apps/conftest.py
import os
import redis
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """
    Fixture that returns an API client with proper configuration
    """
    return APIClient(enforce_csrf_checks=False)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Give all tests access to the database
    """
    pass

@pytest.fixture(scope='session')
def redis_client():
    """
    Fixture that provides a Redis client for testing
    """
    
    host = os.environ.get('REDIS_HOST', 'redis')
    client = redis.Redis(host=host, port=6379, decode_responses=True, db=1)  # Use a separate DB for tests

    # test connectivity
    try:
        client.ping()
    except redis.ConnectionError as e:
        pytest.fail(f"Could not connect to Redis at {host}:6379 - {e}")

    yield client

    # Teardown: flush the test database
    client.flushdb()
    client.close()