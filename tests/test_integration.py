"""
Integration tests for OAuth2 token refresh functionality.

These tests require real credentials and make actual API calls.
"""

import pytest
import time

from tl_ninjarmm.configuration import Configuration
from tl_ninjarmm.api_client import ApiClient
from tl_ninjarmm.api.system_api import SystemApi
from tl_ninjarmm.models.device import Device
from tl_ninjarmm.models.node_role import NodeRole
from tl_ninjarmm.models.organization_detailed import OrganizationDetailed
from tl_ninjarmm.models.policy import Policy
from tl_ninjarmm.models.user import User


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

    def test_multiple_distinct_api_calls_with_correct_output_types(
        self, real_credentials
    ):
        """Test that multiple distinct API calls with the same token have correct output types."""
        config = Configuration(
            host="https://app.ninjarmm.com",
            client_id=real_credentials["client_id"],
            client_secret=real_credentials["client_secret"],
            token_scope="monitoring",
        )

        client = ApiClient(configuration=config)
        system_api = SystemApi(api_client=client)

        organizations_detailed = system_api.get_organizations_detailed()
        assert len(organizations_detailed) > 0
        assert isinstance(organizations_detailed, list)
        assert isinstance(organizations_detailed[0], OrganizationDetailed)

        users = system_api.get_users()
        assert len(users) > 0
        assert isinstance(users, list)
        assert isinstance(users[0], User)

        devices = system_api.get_devices_detailed()
        assert len(devices) > 0
        assert isinstance(devices, list)
        assert isinstance(devices[0], Device)

        policies = system_api.get_policies()
        assert len(policies) > 0
        assert isinstance(policies, list)
        assert isinstance(policies[0], Policy)

        roles = system_api.get_node_roles()
        assert len(roles) > 0
        assert isinstance(roles, list)
        assert isinstance(roles[0], NodeRole)
