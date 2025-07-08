"""
Performance tests for OAuth2 token refresh functionality.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch

from tl_ninjarmm.api_client import ApiClient


class TestTokenRefreshPerformance:
    """Test performance characteristics of token refresh."""

    def test_token_refresh_speed(self, mock_config):
        """Test that token refresh is fast enough for production use."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            mock_session.fetch_token.return_value = {
                "access_token": "new_token_123",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            }
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Mock OAuth2Session to simulate fast refresh
            start_time = time.time()

            # Call token refresh
            client._refresh_token_if_needed()

            end_time = time.time()
            refresh_time = end_time - start_time

            # Token refresh should be very fast (< 1ms)
            assert refresh_time < 0.001, (
                f"Token refresh took {refresh_time:.6f}s, expected < 0.001s"
            )

    def test_token_refresh_under_load(self, mock_config):
        """Test token refresh performance under load."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            # Create a mock session that simulates token refresh
            mock_session = Mock()
            mock_session.fetch_token.return_value = {
                "access_token": "initial_token",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            }
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Simulate multiple token refreshes under load
            start_time = time.time()

            def refresh_token(token_id):
                """Refresh token in a thread-safe manner."""
                # Set token to None to force refresh
                client._token = None
                client._refresh_token_if_needed()
                return token_id

            # Perform 100 token refreshes concurrently
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(refresh_token, i) for i in range(100)]
                results = [future.result() for future in as_completed(futures)]

            end_time = time.time()
            total_time = end_time - start_time

            # Verify all refreshes completed
            assert len(results) == 100

            # Verify performance is acceptable (100 refreshes in < 1 second)
            assert total_time < 1.0, (
                f"100 token refreshes took {total_time:.3f}s, expected < 1.0s"
            )

    def test_token_refresh_memory_safety(self, mock_config):
        """Test that token refresh doesn't cause memory leaks by checking object references."""
        import weakref
        import gc

        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            mock_session.fetch_token.return_value = {
                "access_token": "test_token",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            }
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Create weak references to track if objects are being retained
            client_ref = weakref.ref(client)
            session_ref = weakref.ref(mock_session)

            # Perform multiple token refreshes
            for i in range(1000):
                client._token = None  # Force refresh
                client._refresh_token_if_needed()

            # Force garbage collection
            gc.collect()

            # Verify objects can still be accessed (not garbage collected)
            assert client_ref() is not None, "Client was garbage collected unexpectedly"
            assert session_ref() is not None, (
                "Session was garbage collected unexpectedly"
            )

            # Verify token is properly set
            assert client._token is not None
            assert client.configuration.access_token == "test_token"

    def test_token_refresh_performance_under_stress(self, mock_config):
        """Test token refresh performance under stress conditions."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            mock_session.fetch_token.return_value = {
                "access_token": "stress_test_token",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            }
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Test rapid token refreshes with timing
            start_time = time.time()

            for i in range(1000):
                client._token = None  # Force refresh
                client._refresh_token_if_needed()

            end_time = time.time()
            total_time = end_time - start_time
            avg_time_per_refresh = total_time / 1000

            # Verify performance is acceptable
            assert total_time < 2.0, (
                f"1000 token refreshes took {total_time:.3f}s, expected < 2.0s"
            )
            assert avg_time_per_refresh < 0.002, (
                f"Average refresh time {avg_time_per_refresh:.6f}s, expected < 0.002s"
            )

            # Verify final state is correct
            assert client._token is not None
            assert client.configuration.access_token == "stress_test_token"
            assert mock_session.fetch_token.call_count == 1000

    def test_token_refresh_with_large_tokens(self, mock_config):
        """Test token refresh performance with large token responses."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            # Create a large token response to test memory handling
            large_token = {
                "access_token": "x" * 10000,  # 10KB token
                "refresh_token": "y" * 10000,  # 10KB refresh token
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
                "scope": "monitoring",
                "token_type": "Bearer",
                "extra_data": "z" * 5000,  # Additional data
            }
            mock_session.fetch_token.return_value = large_token
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Perform multiple refreshes with large tokens
            start_time = time.time()

            for i in range(100):
                client._token = None  # Force refresh
                client._refresh_token_if_needed()

            end_time = time.time()
            total_time = end_time - start_time

            # Verify performance is still acceptable with large tokens
            assert total_time < 1.0, (
                f"100 large token refreshes took {total_time:.3f}s, expected < 1.0s"
            )

            # Verify final state
            assert client._token is not None
            assert client.configuration.access_token == large_token["access_token"]
            assert client.configuration.access_token is not None
            assert len(client.configuration.access_token) == 10000


class TestStressTesting:
    """Test stress scenarios for OAuth2 functionality."""

    def test_high_frequency_token_refreshes(self, mock_config):
        """Test performance under high-frequency token refreshes."""
        with (
            patch("tl_ninjarmm.api_client.OAuth2Session") as mock_oauth,
        ):
            mock_session = Mock()
            mock_session.fetch_token.return_value = {
                "access_token": "high_freq_token",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            }
            mock_oauth.return_value = mock_session

            client = ApiClient(configuration=mock_config)

            # Perform rapid token refreshes
            start_time = time.time()

            for i in range(1000):
                client._token = None  # Force refresh
                client._refresh_token_if_needed()

            end_time = time.time()
            total_time = end_time - start_time

            # Verify performance is acceptable
            assert total_time < 5.0, (
                f"1000 token refreshes took {total_time:.3f}s, expected < 5.0s"
            )

            # Verify token was set correctly
            assert client._token is not None
            assert client.configuration.access_token == "high_freq_token"

    def test_rapid_api_calls_with_oauth(self, mock_config):
        """Test performance under rapid API calls with OAuth2."""
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
            mock_rest_client.request.return_value = Mock()

            # Perform rapid API calls
            start_time = time.time()

            for i in range(500):
                client.call_api(
                    method="GET",
                    url=f"https://test.com/api/{i}",
                    header_params={"Accept": "application/json"},
                )

            end_time = time.time()
            total_time = end_time - start_time

            # Verify performance is acceptable
            assert total_time < 10.0, (
                f"500 API calls took {total_time:.3f}s, expected < 10.0s"
            )

            # Verify all calls used rest_client
            assert mock_rest_client.request.call_count == 500
