from fastapi.testclient import TestClient
import pytest
from unittest import mock
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_no_code(client):
    """
    Test the /api/token/issue endpoint without providing a code.
    """
    response = client.post("/api/token/issue")
    assert response.status_code == 422, "Expected HTTP 422 Unprocessable Entity"
    assert "detail" in response.json(), "Expected error details in response"


def test_successful_token_issue(client):
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "mock_access_token", "scope": "repo", "token_type": "bearer"}

    mock_client = mock.AsyncMock()
    mock_client.__aenter__.return_value.post.return_value = mock_response

    with mock.patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/token/issue", json={"code": "mock_code"})

    assert response.status_code == 200, "Expected HTTP 200 OK"
    assert "access_token" in response.json(), "Expected access_token in response"
    assert response.json()["access_token"] == "mock_access_token", "Expected mock access token"


def test_github_api_failure(client):
    mock_response = mock.MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "invalid_grant", "error_description": "Invalid code"}

    mock_client = mock.AsyncMock()
    mock_client.__aenter__.return_value.post.return_value = mock_response

    with mock.patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/token/issue", json={"code": "invalid_code"})

    assert response.status_code == 400, "Expected HTTP 400 Bad Request"
    assert "detail" in response.json(), "Expected error details in response"
    assert response.json()["detail"] == "Failed to get access token: Invalid code", "Expected specific error message"


def test_internal_server_error(client):
    mock_client = mock.AsyncMock()
    mock_client.__aenter__.return_value.post.side_effect = Exception("Internal Server Error")

    with mock.patch("httpx.AsyncClient", return_value=mock_client):
        response = client.post("/api/token/issue", json={"code": "mock_code"})

    assert response.status_code == 500, "Expected HTTP 500 Internal Server Error"
    assert "detail" in response.json(), "Expected error details in response"
