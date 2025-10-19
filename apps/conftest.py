# apps/conftest.py
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