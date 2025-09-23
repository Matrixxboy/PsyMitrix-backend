# tests/test_generation.py
# Tests for the AI response generation endpoint.

from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import uuid

# Point-wise comment: Test that the generation endpoint requires authentication
def test_generate_endpoint_unauthorized(test_client: TestClient):
    response = test_client.post("/api/generate/", params={"prompt": "hello"})
    assert response.status_code == 401  # Unauthorized

# Point-wise comment: Test the generation endpoint with a valid token and mocked models
def test_generate_endpoint_authorized(test_client: TestClient, monkeypatch):
    # --- 1. Setup: Create a user and get a token ---
    unique_email = f"testgen_{uuid.uuid4()}@example.com"
    test_client.post("/api/users/", json={
        "email": unique_email,
        "password": "testpassword",
        "huggingface_adapter_id": "test-adapter"
    })
    login_response = test_client.post("/api/auth/token", data={
        "username": unique_email,
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- 2. Mocking: Mock the ML model functions ---
    # Mock the embedding function
    mock_get_embedding = MagicMock(return_value=[0.1] * 384) # all-MiniLM-L6-v2 has 384 dimensions
    monkeypatch.setattr("api.services.generation_service.get_embedding", mock_get_embedding)

    # Mock the search function
    mock_search_vectors = MagicMock(return_value=[])
    monkeypatch.setattr("api.services.generation_service.search_vectors", mock_search_vectors)

    # Mock the HF model loading
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    mock_get_hf_model = MagicMock(return_value=(mock_model, mock_tokenizer))
    monkeypatch.setattr("api.services.generation_service.get_hf_model", mock_get_hf_model)
    
    # Mock the actual generation call within the service
    mock_generate_response = MagicMock(return_value="This is a mocked response.")
    monkeypatch.setattr("api.services.generation_service.generate_response", mock_generate_response)

    # --- 3. Test: Call the endpoint ---
    prompt = "What is the meaning of life?"
    response = test_client.post("/api/generate/", params={"prompt": prompt}, headers=headers)

    # --- 4. Assertions ---
    assert response.status_code == 200
    assert response.json() == "This is a mocked response."
    
    # Verify that our mocked generation service was called correctly
    mock_generate_response.assert_called_once_with(
        prompt=prompt, 
        user_id=response.request.url.path.split('/')[-1], # This is a bit of a hack to get the user id
        adapter_id="test-adapter"
    )
