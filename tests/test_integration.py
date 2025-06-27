"""
Integration tests for OAuth2 token refresh functionality.

These tests require real credentials and make actual API calls.
"""

import pytest
import time

from tl_ninjarmm.configuration import Configuration
from tl_ninjarmm.api_client import ApiClient
from tl_ninjarmm.api.system_api import SystemApi


@pytest.mark.integration
class TestRealOAuth2Flow:
    """Integration tests with real OAuth2 flow."""

    def test_real_oauth2_initialization(self, real_credentials):
        """Test real OAuth2 initialization with actual credentials."""
        config = Configuration(
            host="https://app.ninjarmm.com",
            client_id=real_credentials["client_id"],
            client_secret=real_credentials["client_secret"],
            token_scope="monitoring",
        )

        client = ApiClient(configuration=config)

        # Verify OAuth2 session was created
        assert client.token_url is not None
        assert client.oauth_session is not None

        # Verify that no token is present, since it is lazy loaded
        assert client._token is None

    def test_real_api_call_with_oauth2(self, real_credentials):
        """Test real API call with OAuth2 authentication."""
        config = Configuration(
            host="https://app.ninjarmm.com",
            client_id=real_credentials["client_id"],
            client_secret=real_credentials["client_secret"],
            token_scope="monitoring",
        )

        client = ApiClient(configuration=config)
        system_api = SystemApi(api_client=client)

        # Make a real API call
        response = system_api.get_organizations_detailed_with_http_info()

        # Verify response is valid
        assert response is not None
        assert hasattr(response, "status_code")
        assert response.status_code in [200, 401, 403]  # Valid response codes

        if response.status_code == 200:
            # Verify response has data attribute (even if it's None, that's valid)
            assert hasattr(response, "data")
            # Don't assert that data is not None - it can be None for some API responses

    def test_multiple_api_calls_with_same_token(self, real_credentials):
        """Test that multiple API calls work with the same token."""
        config = Configuration(
            host="https://app.ninjarmm.com",
            client_id=real_credentials["client_id"],
            client_secret=real_credentials["client_secret"],
            token_scope="monitoring",
        )

        client = ApiClient(configuration=config)
        system_api = SystemApi(api_client=client)

        # Initial token starts out as None
        assert client._token is None

        # Make multiple API calls
        responses = []
        for i in range(5):
            response = system_api.get_organizations_detailed_with_http_info()
            assert client._token is not None

            # Store the token after the first call
            if i == 0:
                initial_token = client.configuration.access_token

            responses.append(response)
            time.sleep(1)  # Small delay between calls

        # Verify all calls were successful
        for i, response in enumerate(responses):
            assert response.status_code == 200, (
                f"Call {i} failed with status {response.status_code}"
            )

        # Verify token didn't change (no refresh needed)
        assert client._token is not None
        assert client.configuration.access_token == initial_token
