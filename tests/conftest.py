# tests/conftest.py
# Pytest configuration and fixtures.

import pytest
from fastapi.testclient import TestClient
from main import app

# Point-wise comment: Create a fixture for the FastAPI test client
@pytest.fixture(scope="module")
def test_client():
    # Create a TestClient instance
    client = TestClient(app)
    yield client  # The test client is yielded to the tests
