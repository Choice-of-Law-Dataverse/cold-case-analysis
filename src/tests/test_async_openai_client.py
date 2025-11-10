"""
Tests for AsyncOpenAI client singleton implementation and agents configuration.
"""
import os
import sys
from pathlib import Path

# Add src to path for imports
# ruff: noqa: E402
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

import agents
import config


def test_async_openai_client_singleton():
    """Test that get_async_openai_client returns the same instance for the same configuration."""
    # Clear the cache to start fresh
    config._async_openai_client_cache.clear()

    # Get client twice with same configuration
    client1, model1 = config.get_async_openai_client()
    client2, model2 = config.get_async_openai_client()

    # Should be the same instance
    assert client1 is client2, "AsyncOpenAI client should be a singleton for the same configuration"
    assert model1 == model2, "Model should be the same"

    # Check that only one client was created
    assert len(config._async_openai_client_cache) == 1, "Should only have one cached async client"


def test_async_openai_client_different_configs():
    """Test that different configurations create different client instances."""
    # Clear the cache to start fresh
    config._async_openai_client_cache.clear()

    # Set initial configuration
    os.environ["OPENAI_TIMEOUT"] = "300"
    os.environ["OPENAI_MAX_RETRIES"] = "3"
    client1, _ = config.get_async_openai_client()

    # Change configuration
    os.environ["OPENAI_TIMEOUT"] = "600"
    os.environ["OPENAI_MAX_RETRIES"] = "5"
    client2, _ = config.get_async_openai_client()

    # Should be different instances
    assert client1 is not client2, "Different configurations should create different async clients"

    # Check that two clients were cached
    assert len(config._async_openai_client_cache) == 2, "Should have two cached async clients with different configs"

    # Reset to original values
    os.environ["OPENAI_TIMEOUT"] = "300"
    os.environ["OPENAI_MAX_RETRIES"] = "3"


def test_async_openai_client_cache_key():
    """Test that the async client cache key is based on timeout and max_retries."""
    # Clear the cache to start fresh
    config._async_openai_client_cache.clear()

    # Create a client
    os.environ["OPENAI_TIMEOUT"] = "300"
    os.environ["OPENAI_MAX_RETRIES"] = "3"
    client, _ = config.get_async_openai_client()

    # Check the cache key
    expected_key = (300.0, 3)
    assert expected_key in config._async_openai_client_cache, f"Cache should contain key {expected_key}"
    assert config._async_openai_client_cache[expected_key] is client, "Cached async client should match returned client"


def test_agents_default_client_configured():
    """Test that the agents library has been configured with a default client."""
    # The config module should have set the default client
    # We can verify this by checking that the async_openai_client exists
    assert config.async_openai_client is not None, "AsyncOpenAI client should be initialized"

    # Verify it has the expected retry configuration
    expected_max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
    assert config.async_openai_client.max_retries == expected_max_retries, \
        f"Client should have max_retries={expected_max_retries}"


if __name__ == "__main__":
    print("Running test_async_openai_client_singleton...")
    test_async_openai_client_singleton()
    print("✓ test_async_openai_client_singleton passed")

    print("\nRunning test_async_openai_client_different_configs...")
    test_async_openai_client_different_configs()
    print("✓ test_async_openai_client_different_configs passed")

    print("\nRunning test_async_openai_client_cache_key...")
    test_async_openai_client_cache_key()
    print("✓ test_async_openai_client_cache_key passed")

    print("\nRunning test_agents_default_client_configured...")
    test_agents_default_client_configured()
    print("✓ test_agents_default_client_configured passed")

    print("\n✅ All async client tests passed!")
