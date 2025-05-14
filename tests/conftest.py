"""
Define fixtures for tests
"""

import pytest
from fastapi.testclient import TestClient

from src.app.main import app


@pytest.fixture
def client():
    """Test client to test API functionality"""
    return TestClient(app=app)
