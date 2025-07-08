"""
Unit tests for OAuth2 token refresh functionality.
"""

import pytest
from unittest.mock import Mock, patch

from tl_ninjarmm.configuration import Configuration
from tl_ninjarmm.api_client import ApiClient

BASE_TIME = 1000000.0


@pytest.fixture
def mock_time():
    with patch("time.time") as mock_time:
        mock_time.return_value = BASE_TIME
        yield mock_time


class TestOAuth2Initialization:
    """Test OAuth2 session initialization."""

    def test_oauth2_session_initialization_with_credentials(self, mock_config):
        """Test that OAuth2Session is properly initialized with credentials."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            # Configure mocks
            mock_session = Mock()
            mock_oauth.return_value = mock_session

            # Create ApiClient
            client = ApiClient(configuration=mock_config)

            # Verify OAuth2Session was created with correct parameters
            mock_oauth.assert_called_once()
            call_args = mock_oauth.call_args

            # Check that OAuth2Session was created without auto-refresh parameters
            assert "auto_refresh_url" not in call_args[1]
            assert "auto_refresh_kwargs" not in call_args[1]
            assert "token_updater" not in call_args[1]

            # Verify lazy loading - token should not be fetched at instantiation
            assert client._token is None
            assert client.configuration.access_token is None

    def test_oauth2_session_not_initialized_without_credentials(self):
        """Test that an error is raised when initializing without credentials."""
        config = Configuration(host="https://test.com")  # No credentials

        # Verify that ApiClient raises ValueError when no credentials are provided
        with pytest.raises(
            ValueError, match="Client ID and client secret are required"
        ):
            ApiClient(configuration=config)


class TestTokenRefresh:
    """Test token refresh functionality."""

    def test_refresh_token_if_needed_fetches_token_when_none(
        self, mock_config, mock_time
    ):
        """Test that _refresh_token_if_needed fetches token when none exists."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            expected_token = {
                "access_token": "initial_token_123",
                "expires_in": 3600,
                "expires_at": BASE_TIME + 3600,  # BASE_TIME + 3600
            }
            mock_session.fetch_token.return_value = expected_token
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Initially no token should be fetched
            assert client._token is None
            assert client.configuration.access_token is None

            # Call _refresh_token_if_needed
            client._refresh_token_if_needed()

            # Verify token was fetched
            mock_session.fetch_token.assert_called_once()
            assert client._token == expected_token
            assert client.configuration.access_token == expected_token["access_token"]

    def test_refresh_token_if_needed_refreshes_expired_token(
        self, mock_config, mock_time
    ):
        """Test that _refresh_token_if_needed refreshes expired token."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()

            expired_token = {
                "access_token": "expired_token",
                "expires_in": 3600,
                "expires_at": BASE_TIME + 60,  # BASE_TIME + 60 seconds
            }
            new_token = {
                "access_token": "new_token_456",
                "expires_in": 3600,
                "expires_at": BASE_TIME + 3600,  # BASE_TIME + 3600
            }
            mock_session.fetch_token.return_value = expired_token
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)
            client._refresh_token_if_needed()

            assert client._token == expired_token
            assert client.configuration.access_token == expired_token["access_token"]

            # Mock time to be after expiry (with skew)
            mock_session.fetch_token.return_value = new_token
            mock_time.return_value = (
                expired_token["expires_at"] - 30
            )  # 30 seconds before expiry, but within skew

            client._refresh_token_if_needed()

            assert client._token == new_token
            assert client.configuration.access_token == new_token["access_token"]

    def test_refresh_token_if_needed_skips_refresh_for_valid_token(
        self, mock_config, mock_time
    ):
        """Test that _refresh_token_if_needed skips refresh for valid token."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()

            valid_token = {
                "access_token": "valid_token",
                "expires_in": 3600,
                "expires_at": BASE_TIME + 3600,  # BASE_TIME + 3600
            }
            mock_session.fetch_token.return_value = valid_token
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)
            client._token = valid_token
            client.configuration.access_token = valid_token["access_token"]

            # Mock time to be well before expiry
            mock_time.return_value = (
                valid_token["expires_at"] - 120
            )  # 2 minutes before expiry

            # Call _refresh_token_if_needed
            client._refresh_token_if_needed()

            # Verify token was not refreshed
            mock_session.fetch_token.assert_not_called()
            assert client._token == valid_token
            assert client.configuration.access_token == valid_token["access_token"]

    def test_refresh_token_if_needed_handles_invalid_token_response(self, mock_config):
        """Test that _refresh_token_if_needed handles invalid token response."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            # Return invalid token (missing access_token)
            invalid_token = {"expires_in": 3600}
            mock_session.fetch_token.return_value = invalid_token
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Call _refresh_token_if_needed
            client._refresh_token_if_needed()

            # Verify token was fetched but access_token is None
            mock_session.fetch_token.assert_called_once()
            assert client._token == invalid_token
            assert client.configuration.access_token is None


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_refresh_token_if_needed_handles_missing_token_url(self, mock_config):
        """Test that _refresh_token_if_needed handles missing token_url."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            mock_oauth.return_value = mock_session

            # Simulate missing token_url
            client = ApiClient(configuration=mock_config)
            client.token_url = None  # type: ignore[assignment]

            # Should not raise any exceptions
            client._refresh_token_if_needed()

            # Verify no token fetch was attempted
            mock_session.fetch_token.assert_not_called()

    def test_call_api_handles_exceptions(self, mock_config):
        """Test that call_api properly handles exceptions."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
            patch.object(ApiClient, "_refresh_token_if_needed"),
        ):
            mock_session = Mock()
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)
            # Mock the rest_client directly on the instance
            mock_rest_client = Mock()
            client.rest_client = mock_rest_client
            mock_rest_client.request.side_effect = Exception("Test exception")

            # Call call_api should raise the exception
            with pytest.raises(Exception, match="Test exception"):
                client.call_api("GET", "https://test.com/api")
