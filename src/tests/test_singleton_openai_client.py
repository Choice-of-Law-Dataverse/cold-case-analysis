"""
Tests for singleton OpenAI client implementation.
"""
import os
import sys
from pathlib import Path

# Add src to path for imports - this is necessary for test files
# ruff: noqa: E402
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

import config


def test_openai_client_singleton():
    """Test that get_openai_client returns the same instance for the same configuration."""
    # Clear the cache to start fresh
    config._openai_client_cache.clear()

    # Get client twice with same configuration
    client1, model1 = config.get_openai_client()
    client2, model2 = config.get_openai_client()

    # Should be the same instance
    assert client1 is client2, "OpenAI client should be a singleton for the same configuration"
    assert model1 == model2, "Model should be the same"

    # Check that only one client was created
    assert len(config._openai_client_cache) == 1, "Should only have one cached client"


def test_openai_client_different_configs():
    """Test that different configurations create different client instances."""
    # Clear the cache to start fresh
    config._openai_client_cache.clear()

    # Set initial configuration
    os.environ["OPENAI_TIMEOUT"] = "300"
    os.environ["OPENAI_MAX_RETRIES"] = "3"
    client1, _ = config.get_openai_client()

    # Change configuration
    os.environ["OPENAI_TIMEOUT"] = "600"
    os.environ["OPENAI_MAX_RETRIES"] = "5"
    client2, _ = config.get_openai_client()

    # Should be different instances
    assert client1 is not client2, "Different configurations should create different clients"

    # Check that two clients were cached
    assert len(config._openai_client_cache) == 2, "Should have two cached clients with different configs"

    # Reset to original values
    os.environ["OPENAI_TIMEOUT"] = "300"
    os.environ["OPENAI_MAX_RETRIES"] = "3"


def test_openai_client_cache_key():
    """Test that the cache key is based on timeout and max_retries."""
    # Clear the cache to start fresh
    config._openai_client_cache.clear()

    # Create a client
    os.environ["OPENAI_TIMEOUT"] = "300"
    os.environ["OPENAI_MAX_RETRIES"] = "3"
    client, _ = config.get_openai_client()

    # Check the cache key
    expected_key = (300.0, 3)
    assert expected_key in config._openai_client_cache, f"Cache should contain key {expected_key}"
    assert config._openai_client_cache[expected_key] is client, "Cached client should match returned client"


if __name__ == "__main__":
    print("Running test_openai_client_singleton...")
    test_openai_client_singleton()
    print("✓ test_openai_client_singleton passed")

    print("\nRunning test_openai_client_different_configs...")
    test_openai_client_different_configs()
    print("✓ test_openai_client_different_configs passed")

    print("\nRunning test_openai_client_cache_key...")
    test_openai_client_cache_key()
    print("✓ test_openai_client_cache_key passed")

    print("\n✅ All tests passed!")
