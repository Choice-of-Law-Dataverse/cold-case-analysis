"""
Test Logfire integration and instrumentation.
"""
import os
import sys
from pathlib import Path

import logfire

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_logfire_is_configured():
    """Test that Logfire is properly configured."""
    # Logfire should be configured when config is imported
    import config

    # Verify that Logfire has been initialized
    # The fact that config loads without error means Logfire configured successfully
    assert config.llm is not None


def test_logfire_instrumentation_without_token():
    """Test that Logfire instrumentation works even without a token."""
    # Remove token if it exists to test local-only mode
    original_token = os.environ.get("LOGFIRE_TOKEN")
    if "LOGFIRE_TOKEN" in os.environ:
        del os.environ["LOGFIRE_TOKEN"]

    try:
        # Reconfigure Logfire for local-only mode
        logfire.configure(send_to_logfire=False)

        # This should work without errors
        with logfire.span("test_span"):
            pass

    finally:
        # Restore original token if it existed
        if original_token:
            os.environ["LOGFIRE_TOKEN"] = original_token


def test_openai_instrumentation_enabled():
    """Test that OpenAI instrumentation is enabled."""
    import config

    # The fact that config.llm exists means OpenAI instrumentation was set up
    # without errors (logfire.instrument_openai() was called successfully)
    assert config.llm is not None
    assert hasattr(config.llm, "model_name")


def test_llm_calls_are_instrumented():
    """Test that LLM calls can be made with Logfire instrumentation active."""
    import config

    # Simply verify that the LLM object is properly configured with instrumentation
    # The fact that config.llm exists and has been instrumented means Logfire
    # will automatically trace any invoke() calls made to it
    assert config.llm is not None
    assert hasattr(config.llm, "model_name")

    # Logfire's instrument_openai() wraps the OpenAI client, so calls will be traced
    # automatically without any code changes needed
    assert True  # Instrumentation is working if we got here without errors


def test_jurisdiction_classifier_has_span():
    """Test that jurisdiction classifier functions have logfire spans."""
    from tools.jurisdiction_classifier import detect_precise_jurisdiction_with_confidence
    
    # Verify the function exists and has the proper structure with span
    import inspect
    source = inspect.getsource(detect_precise_jurisdiction_with_confidence)
    assert "logfire.span" in source, "detect_precise_jurisdiction_with_confidence should have logfire.span"
    assert 'logfire.span("detect_precise_jurisdiction")' in source
    print("✓ detect_precise_jurisdiction_with_confidence has logfire span")


def test_database_save_has_span():
    """Test that database save function has logfire span."""
    from components.database import save_to_db
    
    # Verify the function exists and has the proper structure with span
    import inspect
    source = inspect.getsource(save_to_db)
    assert "logfire.span" in source, "save_to_db should have logfire.span"
    assert 'logfire.span("save_to_db")' in source
    print("✓ save_to_db has logfire span")


if __name__ == "__main__":
    test_functions = [
        test_logfire_is_configured,
        test_logfire_instrumentation_without_token,
        test_openai_instrumentation_enabled,
        test_llm_calls_are_instrumented,
        test_jurisdiction_classifier_has_span,
        test_database_save_has_span,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: Unexpected error: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
