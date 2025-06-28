"""
Performance tests for OAuth2 token refresh functionality.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch

from tl_ninjarmm.api_client import ApiClient


class TestTokenRefreshPerformance:
    """Test performance characteristics of token refresh."""

    def test_token_refresh_speed(self, api_client_with_oauth):
        """Test that token refresh is fast enough for production use."""
        client = api_client_with_oauth

        # Mock OAuth2Session to simulate fast refresh
        start_time = time.time()

        new_token = {
            "access_token": "new_token_123",
            "expires_in": 3600,
            "expires_at": time.time() + 3600,
        }

        # Call token updater
        client._token_updater(new_token)

        end_time = time.time()
        refresh_time = end_time - start_time

        # Token update should be very fast (< 1ms)
        assert refresh_time < 0.001, (
            f"Token refresh took {refresh_time:.6f}s, expected < 0.001s"
        )

    def test_concurrent_api_calls_with_oauth(
        self, api_client_with_oauth, mock_requests_response
    ):
        """Test that concurrent API calls work correctly with OAuth2."""
        client = api_client_with_oauth
        client.oauth_session.request.return_value = mock_requests_response

        with patch("tl_ninjarmm.api_client.rest.RESTResponse") as mock_rest_response:
            mock_rest_response.return_value = Mock()

            def make_api_call(call_id):
                """Make a single API call."""
                start_time = time.time()
                response = client.call_api(
                    method="GET",
                    url=f"https://test.com/api/{call_id}",
                    header_params={"Accept": "application/json"},
                )
                end_time = time.time()
                return {
                    "call_id": call_id,
                    "response": response,
                    "duration": end_time - start_time,
                }

            # Make 10 concurrent API calls
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_api_call, i) for i in range(10)]
                results = [future.result() for future in as_completed(futures)]

            # Verify all calls completed successfully
            assert len(results) == 10

            # Verify all calls used OAuth2Session
            assert client.oauth_session.request.call_count == 10

            # Verify response times are reasonable (< 1 second each)
            for result in results:
                assert result["duration"] < 1.0, (
                    f"Call {result['call_id']} took {result['duration']:.3f}s"
                )

    def test_token_refresh_under_load(self, mock_config):
        """Test token refresh performance under load."""
        with (
            patch("tl_ninjarmm.api_client.BackendApplicationClient"),
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

            # Simulate multiple token updates under load
            start_time = time.time()

            def update_token(token_id):
                """Update token in a thread-safe manner."""
                new_token = {
                    "access_token": f"token_{token_id}",
                    "expires_in": 3600,
                    "expires_at": time.time() + 3600,
                }
                client._token_updater(new_token)
                return token_id

            # Perform 100 token updates concurrently
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(update_token, i) for i in range(100)]
                results = [future.result() for future in as_completed(futures)]

            end_time = time.time()
            total_time = end_time - start_time

            # Verify all updates completed
            assert len(results) == 100

            # Verify performance is acceptable (100 updates in < 1 second)
            assert total_time < 1.0, (
                f"100 token updates took {total_time:.3f}s, expected < 1.0s"
            )

    def test_memory_usage_during_refresh(self, api_client_with_oauth):
        """Test that token refresh doesn't cause memory leaks."""
        import gc

        client = api_client_with_oauth

        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform multiple token updates
        for i in range(1000):
            new_token = {
                "access_token": f"token_{i}",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            }
            client._token_updater(new_token)

        # Get final memory usage
        gc.collect()
        final_objects = len(gc.get_objects())

        # Memory usage should not increase significantly
        object_increase = final_objects - initial_objects
        assert object_increase < 100, (
            f"Object count increased by {object_increase}, expected < 100"
        )

    def test_api_call_latency_with_oauth(
        self, api_client_with_oauth, mock_requests_response
    ):
        """Test that API calls with OAuth2 don't add significant latency."""
        client = api_client_with_oauth
        client.oauth_session.request.return_value = mock_requests_response

        with patch("tl_ninjarmm.api_client.rest.RESTResponse") as mock_rest_response:
            mock_rest_response.return_value = Mock()

            # Measure latency for multiple API calls
            latencies = []

            for i in range(50):
                start_time = time.time()
                client.call_api(
                    method="GET",
                    url=f"https://test.com/api/{i}",
                    header_params={"Accept": "application/json"},
                )
                end_time = time.time()
                latencies.append(end_time - start_time)

            # Calculate statistics
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)

            # Average latency should be very low (< 10ms)
            assert avg_latency < 0.01, (
                f"Average latency {avg_latency:.6f}s, expected < 0.01s"
            )

            # Maximum latency should be reasonable (< 50ms)
            assert max_latency < 0.05, (
                f"Maximum latency {max_latency:.6f}s, expected < 0.05s"
            )


class TestConcurrencyAndThreadSafety:
    """Test concurrency and thread safety of OAuth2 functionality."""

    def test_thread_safe_token_updater(self, api_client_with_oauth):
        """Test that token updater is thread-safe."""
        client = api_client_with_oauth

        # Create multiple threads that update tokens simultaneously
        def update_token_thread(thread_id):
            """Update token from a thread."""
            for i in range(100):
                new_token = {
                    "access_token": f"thread_{thread_id}_token_{i}",
                    "expires_in": 3600,
                    "expires_at": time.time() + 3600,
                }
                client._token_updater(new_token)
                time.sleep(0.001)  # Small delay to increase contention

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=update_token_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify final state is consistent
        assert client.token is not None
        assert client.configuration.access_token is not None
        assert len(client.configuration.access_token) > 0

    def test_concurrent_api_calls_thread_safety(
        self, api_client_with_oauth, mock_requests_response
    ):
        """Test that concurrent API calls are thread-safe."""
        client = api_client_with_oauth
        client.oauth_session.request.return_value = mock_requests_response

        with patch("tl_ninjarmm.api_client.rest.RESTResponse") as mock_rest_response:
            mock_rest_response.return_value = Mock()

            # Track successful calls
            successful_calls = []
            failed_calls = []

            def api_call_thread(thread_id):
                """Make API calls from a thread."""
                for i in range(20):
                    try:
                        start_time = time.time()
                        response = client.call_api(
                            method="GET",
                            url=f"https://test.com/api/thread_{thread_id}_{i}",
                            header_params={"Accept": "application/json"},
                        )
                        end_time = time.time()

                        successful_calls.append(
                            {
                                "thread_id": thread_id,
                                "call_id": i,
                                "duration": end_time - start_time,
                                "response": response,
                            }
                        )
                    except Exception as e:
                        failed_calls.append(
                            {"thread_id": thread_id, "call_id": i, "error": str(e)}
                        )

            # Start multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=api_call_thread, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify all calls were successful
            assert len(successful_calls) == 100  # 5 threads * 20 calls each
            assert len(failed_calls) == 0, f"Failed calls: {failed_calls}"

            # Verify all calls used OAuth2Session
            assert client.oauth_session.request.call_count == 100

    def test_token_refresh_race_condition_handling(self, api_client_with_oauth):
        """Test that token refresh handles race conditions gracefully."""
        client = api_client_with_oauth

        # Simulate multiple threads trying to refresh token simultaneously
        refresh_events = []

        def refresh_token_thread(thread_id):
            """Simulate token refresh from a thread."""
            for i in range(10):
                new_token = {
                    "access_token": f"refresh_{thread_id}_{i}",
                    "expires_in": 3600,
                    "expires_at": time.time() + 3600,
                }

                # Simulate some processing time to increase chance of race conditions
                time.sleep(0.001)

                client._token_updater(new_token)
                refresh_events.append(
                    {
                        "thread_id": thread_id,
                        "iteration": i,
                        "token": new_token["access_token"],
                    }
                )

        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=refresh_token_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all refresh events were processed
        assert len(refresh_events) == 100  # 10 threads * 10 iterations each

        # Verify final state is consistent
        assert client.token is not None
        assert client.configuration.access_token is not None


class TestStressTesting:
    """Stress tests for OAuth2 functionality."""

    def test_high_frequency_token_updates(self, api_client_with_oauth):
        """Test handling of high-frequency token updates."""
        client = api_client_with_oauth

        start_time = time.time()

        # Perform 1000 token updates rapidly
        for i in range(1000):
            new_token = {
                "access_token": f"rapid_token_{i}",
                "expires_in": 3600,
                "expires_at": time.time() + 3600,
            }
            client._token_updater(new_token)

        end_time = time.time()
        total_time = end_time - start_time

        # Should handle 1000 updates quickly
        assert total_time < 2.0, (
            f"1000 token updates took {total_time:.3f}s, expected < 2.0s"
        )

        # Verify final state
        assert client.token is not None
        assert client.configuration.access_token == "rapid_token_999"

    def test_rapid_api_calls_with_oauth(
        self, api_client_with_oauth, mock_requests_response
    ):
        """Test handling of rapid API calls with OAuth2."""
        client = api_client_with_oauth
        client.oauth_session.request.return_value = mock_requests_response

        with patch("tl_ninjarmm.api_client.rest.RESTResponse") as mock_rest_response:
            mock_rest_response.return_value = Mock()

            start_time = time.time()

            # Make 500 rapid API calls
            for i in range(500):
                client.call_api(
                    method="GET",
                    url=f"https://test.com/api/rapid_{i}",
                    header_params={"Accept": "application/json"},
                )

            end_time = time.time()
            total_time = end_time - start_time

            # Should handle 500 calls quickly
            assert total_time < 5.0, (
                f"500 API calls took {total_time:.3f}s, expected < 5.0s"
            )

            # Verify all calls were made
            assert client.oauth_session.request.call_count == 500

    def test_mixed_workload_performance(
        self, api_client_with_oauth, mock_requests_response
    ):
        """Test performance under mixed workload (API calls + token updates)."""
        client = api_client_with_oauth
        client.oauth_session.request.return_value = mock_requests_response

        with patch("tl_ninjarmm.api_client.rest.RESTResponse") as mock_rest_response:
            mock_rest_response.return_value = Mock()

            def mixed_workload_thread(thread_id):
                """Perform mixed workload in a thread."""
                for i in range(50):
                    # Make API call
                    client.call_api(
                        method="GET",
                        url=f"https://test.com/api/mixed_{thread_id}_{i}",
                        header_params={"Accept": "application/json"},
                    )

                    # Update token
                    new_token = {
                        "access_token": f"mixed_token_{thread_id}_{i}",
                        "expires_in": 3600,
                        "expires_at": time.time() + 3600,
                    }
                    client._token_updater(new_token)

            start_time = time.time()

            # Start multiple threads with mixed workload
            threads = []
            for i in range(5):
                thread = threading.Thread(target=mixed_workload_thread, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            end_time = time.time()
            total_time = end_time - start_time

            # Should handle mixed workload efficiently
            assert total_time < 10.0, (
                f"Mixed workload took {total_time:.3f}s, expected < 10.0s"
            )

            # Verify all API calls were made
            assert (
                client.oauth_session.request.call_count == 250
            )  # 5 threads * 50 calls each
