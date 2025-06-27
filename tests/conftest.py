"""
Pytest configuration and fixtures for tl-ninjarmm tests.
"""

import os
import pytest
from unittest.mock import Mock, patch
import time

from tl_ninjarmm.configuration import Configuration
from tl_ninjarmm.api_client import ApiClient


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return Configuration(
        host="https://test.ninjarmm.com",
        client_id="test_client_id",
        client_secret="test_client_secret",
        token_scope="monitoring",
    )


@pytest.fixture
def mock_token():
    """Mock OAuth2 token for testing."""
    return {
        "access_token": "test_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": time.time() + 3600,
        "scope": "monitoring",
    }


@pytest.fixture
def expired_token():
    """Mock expired OAuth2 token for testing."""
    return {
        "access_token": "expired_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": time.time() - 3600,  # Expired 1 hour ago
        "scope": "monitoring",
    }


@pytest.fixture
def mock_oauth_session():
    """Mock OAuth2Session for testing."""
    session = Mock()
    session.token = {
        "access_token": "test_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": time.time() + 3600,
        "scope": "monitoring",
    }
    return session


@pytest.fixture
def mock_requests_response():
    """Mock requests response for testing."""
    response = Mock()
    response.status_code = 200
    response.content = b'{"data": "test"}'
    response.headers = {"Content-Type": "application/json"}
    response.reason = "OK"
    return response


@pytest.fixture
def api_client_with_oauth(mock_config):
    """ApiClient instance with OAuth2 configured."""
    with (
        patch("tl_ninjarmm.api_client.BackendApplicationClient"),
        patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
    ):
        # Configure the mock OAuth2Session
        mock_session = Mock()
        mock_session.fetch_token.return_value = {
            "access_token": "test_access_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600,
            "expires_at": time.time() + 3600,
            "scope": "monitoring",
        }
        mock_oauth.return_value = mock_session

        client = ApiClient(configuration=mock_config)

        return client


@pytest.fixture
def api_client_without_oauth():
    """ApiClient instance without OAuth2 configured."""
    config = Configuration(host="https://test.ninjarmm.com")
    return ApiClient(configuration=config)


@pytest.fixture
def real_credentials():
    """Get real credentials from environment for integration tests."""
    client_id = os.environ.get("NINJA_CLIENT_ID")
    client_secret = os.environ.get("NINJA_CLIENT_SECRET")

    if not client_id or not client_secret:
        pytest.skip(
            "NINJA_CLIENT_ID and NINJA_CLIENT_SECRET environment variables required"
        )

    return {
        "client_id": client_id,
        "client_secret": client_secret,
    }
