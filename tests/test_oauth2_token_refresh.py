"""
Unit tests for OAuth2 token refresh functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch

from tl_ninjarmm.configuration import Configuration
from tl_ninjarmm.api_client import ApiClient, RequestsResponseAdapter


class TestOAuth2Initialization:
    """Test OAuth2 session initialization."""

    def test_oauth2_session_initialization_with_credentials(self, mock_config):
        """Test that OAuth2Session is properly initialized with credentials."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            # Configure mocks
            mock_session = Mock()
            mock_session.fetch_token.return_value = {
                "access_token": "test_token",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            }
            mock_oauth.return_value = mock_session

            # Create ApiClient
            client = ApiClient(configuration=mock_config)

            # Verify OAuth2Session was created with correct parameters
            mock_oauth.assert_called_once()
            call_args = mock_oauth.call_args

            # Check that auto_refresh_url is set
            assert (
                call_args[1]["auto_refresh_url"] == f"{mock_config.host}/ws/oauth/token"
            )

            # Check that auto_refresh_kwargs contains credentials
            assert (
                call_args[1]["auto_refresh_kwargs"]["client_id"]
                == mock_config.client_id
            )
            assert (
                call_args[1]["auto_refresh_kwargs"]["client_secret"]
                == mock_config.client_secret
            )

            # Check that token_updater is set
            assert call_args[1]["token_updater"] == client._token_updater

    def test_oauth2_session_not_initialized_without_credentials(self):
        """Test that OAuth2Session is not initialized without credentials."""
        config = Configuration(host="https://test.com")  # No credentials

        with (
            patch("tl_ninjarmm.api_client.BackendApplicationClient"),
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            client = ApiClient(configuration=config)

            # Verify OAuth2Session was not called
            mock_oauth.assert_not_called()

            # Verify oauth_session attribute doesn't exist
            assert not hasattr(client, "oauth_session")

    def test_initial_token_fetch(self, mock_config):
        """Test that initial token is fetched and stored correctly."""
        with (
            patch("tl_ninjarmm.api_client.BackendApplicationClient"),
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            expected_token = {
                "access_token": "initial_token_123",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            }
            mock_session.fetch_token.return_value = expected_token
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Verify token was fetched
            mock_session.fetch_token.assert_called_once()

            # Verify token was stored
            assert client.token == expected_token
            assert client.configuration.access_token == expected_token["access_token"]


class TestTokenUpdater:
    """Test token updater functionality."""

    def test_token_updater_updates_internal_token(self, api_client_with_oauth):
        """Test that token updater updates internal token."""
        client = api_client_with_oauth

        new_token = {
            "access_token": "new_token_456",
            "expires_in": 3600,
            "expires_at": time.time() + 3600,
        }

        # Call token updater
        client._token_updater(new_token)

        # Verify token was updated
        assert client.token == new_token
        assert client.configuration.access_token == new_token["access_token"]

    def test_token_updater_updates_configuration(self, api_client_with_oauth):
        """Test that token updater updates configuration access token."""
        client = api_client_with_oauth

        new_token = {
            "access_token": "updated_token_789",
            "expires_in": 3600,
            "expires_at": time.time() + 3600,
        }

        # Call token updater
        client._token_updater(new_token)

        # Verify configuration was updated
        assert client.configuration.access_token == new_token["access_token"]

    def test_token_updater_handles_invalid_token(self, api_client_with_oauth):
        """Test that token updater handles invalid token data."""
        client = api_client_with_oauth

        # Test with None token
        client._token_updater(None)
        assert client.token is None
        assert client.configuration.access_token is None

        # Test with token missing access_token
        invalid_token = {"expires_in": 3600}
        client._token_updater(invalid_token)
        assert client.token == invalid_token
        assert client.configuration.access_token is None

        # Test with valid token
        valid_token = {"access_token": "new_token_123", "expires_in": 3600}
        client._token_updater(valid_token)
        assert client.token == valid_token
        assert client.configuration.access_token == "new_token_123"


class TestRequestsResponseAdapter:
    """Test the RequestsResponseAdapter class."""

    def test_adapter_initialization(self, mock_requests_response):
        """Test that adapter properly wraps requests response."""
        adapter = RequestsResponseAdapter(mock_requests_response)

        assert adapter.status == mock_requests_response.status_code
        assert adapter.reason == mock_requests_response.reason
        assert adapter.data == mock_requests_response.content
        assert adapter.headers == mock_requests_response.headers

    def test_adapter_getheaders(self, mock_requests_response):
        """Test getheaders method."""
        adapter = RequestsResponseAdapter(mock_requests_response)

        headers = adapter.getheaders()
        assert headers == mock_requests_response.headers

    def test_adapter_getheader(self, mock_requests_response):
        """Test getheader method."""
        adapter = RequestsResponseAdapter(mock_requests_response)

        # Test existing header
        content_type = adapter.getheader("Content-Type")
        assert content_type == "application/json"

        # Test non-existing header with default
        non_existent = adapter.getheader("Non-Existent", "default_value")
        assert non_existent == "default_value"


class TestCallApiWithOAuth2:
    """Test call_api method with OAuth2 session."""

    def test_call_api_uses_oauth_session_when_available(
        self, api_client_with_oauth, mock_requests_response
    ):
        """Test that call_api uses OAuth2Session when available."""
        client = api_client_with_oauth

        # Mock the OAuth2Session request method
        client.oauth_session.request.return_value = mock_requests_response

        # Mock rest.RESTResponse
        with patch("tl_ninjarmm.api_client.rest.RESTResponse") as mock_rest_response:
            mock_rest_response.return_value = Mock()

            # Make API call, really just to assess that the call_args for the oauth_session.request are correct
            client.call_api(
                method="GET",
                url="https://test.com/api",
                header_params={"Accept": "application/json"},
            )

            # Verify OAuth2Session was used
            client.oauth_session.request.assert_called_once()
            call_args = client.oauth_session.request.call_args

            assert call_args[1]["method"] == "GET"
            assert call_args[1]["url"] == "https://test.com/api"
            assert call_args[1]["headers"] == {"Accept": "application/json"}

    def test_call_api_falls_back_to_rest_client_without_oauth(
        self, api_client_without_oauth
    ):
        """Test that call_api falls back to rest_client without OAuth2."""
        client = api_client_without_oauth

        # Mock rest_client.request properly
        mock_response = Mock()
        with patch.object(
            client.rest_client, "request", return_value=mock_response
        ) as mock_request:
            # Make API call
            result = client.call_api(
                method="GET",
                url="https://test.com/api",
                header_params={"Accept": "application/json"},
            )

            # Verify rest_client was used
            mock_request.assert_called_once()

            # Verify result is the mock response
            assert result == mock_response

    def test_call_api_handles_json_body(
        self, api_client_with_oauth, mock_requests_response
    ):
        """Test that call_api properly handles JSON body."""
        client = api_client_with_oauth
        client.oauth_session.request.return_value = mock_requests_response

        with patch("tl_ninjarmm.api_client.rest.RESTResponse") as mock_rest_response:
            mock_rest_response.return_value = Mock()

            json_body = {"key": "value"}

            client.call_api(
                method="POST",
                url="https://test.com/api",
                body=json_body,
                header_params={"Content-Type": "application/json"},
            )

            call_args = client.oauth_session.request.call_args
            assert call_args[1]["json"] == json_body
            assert call_args[1]["data"] == json_body

    def test_call_api_handles_string_body(
        self, api_client_with_oauth, mock_requests_response
    ):
        """Test that call_api properly handles string body."""
        client = api_client_with_oauth
        client.oauth_session.request.return_value = mock_requests_response

        with patch("tl_ninjarmm.api_client.rest.RESTResponse") as mock_rest_response:
            mock_rest_response.return_value = Mock()

            string_body = "test data"

            client.call_api(
                method="POST",
                url="https://test.com/api",
                body=string_body,
                header_params={"Content-Type": "text/plain"},
            )

            call_args = client.oauth_session.request.call_args
            assert call_args[1]["data"] == string_body
            assert call_args[1]["json"] is None


class TestAutomaticTokenRefresh:
    """Test automatic token refresh behavior."""

    def test_oauth_session_auto_refresh_configuration(self, mock_config):
        """Test that OAuth2Session is configured for automatic refresh."""
        with (
            patch("tl_ninjarmm.api_client.BackendApplicationClient"),
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            # Configure the mock session to return a proper token dictionary
            mock_session.fetch_token.return_value = {
                "access_token": "test_access_token_12345",
                "token_type": "Bearer",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
                "scope": "monitoring",
            }
            mock_oauth.return_value = mock_session

            # create the client so that it triggers the token refresh
            client = ApiClient(configuration=mock_config)  # noqa: F841

            # Verify OAuth2Session was configured with auto_refresh_url
            call_args = mock_oauth.call_args
            assert (
                call_args[1]["auto_refresh_url"] == f"{mock_config.host}/ws/oauth/token"
            )

            # Verify auto_refresh_kwargs contains credentials
            refresh_kwargs = call_args[1]["auto_refresh_kwargs"]
            assert refresh_kwargs["client_id"] == mock_config.client_id
            assert refresh_kwargs["client_secret"] == mock_config.client_secret

    def test_token_updater_callback_registered(self, mock_config):
        """Test that token updater callback is properly registered."""
        with (
            patch("tl_ninjarmm.api_client.BackendApplicationClient"),
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            # Configure the mock session to return a proper token dictionary
            mock_session.fetch_token.return_value = {
                "access_token": "test_access_token_12345",
                "token_type": "Bearer",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
                "scope": "monitoring",
            }
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Verify token_updater was registered
            call_args = mock_oauth.call_args
            assert call_args[1]["token_updater"] == client._token_updater

    @patch("time.time")
    def test_token_refresh_on_expiry(
        self, mock_time, api_client_with_oauth, mock_requests_response
    ):
        """Test that token is refreshed when expired."""
        # Set current time to after token expiry
        mock_time.return_value = time.time() + 7200  # 2 hours from now

        client = api_client_with_oauth

        # Configure the mock token as a proper dictionary that can be modified
        client.oauth_session.token = {
            "access_token": "test_access_token_12345",
            "token_type": "Bearer",
            "expires_in": 3600,
            "expires_at": time.time() - 3600,  # Expired 1 hour ago
            "scope": "monitoring",
        }

        # Mock OAuth2Session request to simulate refresh
        client.oauth_session.request.return_value = mock_requests_response

        with patch("tl_ninjarmm.api_client.rest.RESTResponse") as mock_rest_response:
            mock_rest_response.return_value = Mock()

            # Make API call - this should trigger refresh
            client.call_api(method="GET", url="https://test.com/api")

            # Verify OAuth2Session request was called (refresh should happen automatically)
            assert client.oauth_session.request.called


class TestErrorHandling:
    """Test error handling in OAuth2 functionality."""

    def test_call_api_handles_oauth_exceptions(self, api_client_with_oauth):
        """Test that call_api properly handles OAuth2 exceptions."""
        client = api_client_with_oauth

        # Mock OAuth2Session to raise an exception
        client.oauth_session.request.side_effect = Exception("OAuth2 error")

        # Should raise the exception
        with pytest.raises(Exception, match="OAuth2 error"):
            client.call_api(method="GET", url="https://test.com/api")
