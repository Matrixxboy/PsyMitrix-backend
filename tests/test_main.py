# tests/test_main.py
# Tests for the main application and authentication flow.

from fastapi.testclient import TestClient
import uuid

# Point-wise comment: Test for the root endpoint
def test_root_endpoint(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to PsyMitrix AI Backend"}

# Point-wise comment: Test for the user creation endpoint
def test_create_user(test_client: TestClient):
    # Generate a unique email for each test run
    unique_email = f"testuser_{uuid.uuid4()}@example.com"
    response = test_client.post("/api/users/", json={
        "email": unique_email,
        "password": "testpassword",
        "huggingface_adapter_id": "test-adapter"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == unique_email
    assert "hashed_password" in data

# Point-wise comment: Test for the token generation endpoint (login)
def test_login_for_access_token(test_client: TestClient):
    # Create a user first
    unique_email = f"testlogin_{uuid.uuid4()}@example.com"
    test_client.post("/api/users/", json={
        "email": unique_email,
        "password": "testpassword",
        "huggingface_adapter_id": "test-adapter"
    })
    
    # Attempt to log in
    response = test_client.post("/api/auth/token", data={
        "username": unique_email,
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
