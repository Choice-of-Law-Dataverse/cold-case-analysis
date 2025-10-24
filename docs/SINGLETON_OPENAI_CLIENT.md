# Singleton OpenAI Client Implementation

## Overview
This document describes the singleton pattern implementation for the OpenAI client in the CoLD Case Analysis project.

## Problem Statement
Previously, every call to `get_openai_client()` created a new `OpenAI` instance, which resulted in:
- Multiple httpx connection pools
- Inefficient resource usage
- Multiple TCP connections to OpenAI's API
- Potential connection errors under load
- No connection reuse benefits

## Solution
Implemented a singleton pattern that caches OpenAI client instances based on their configuration (timeout, max_retries).

## Implementation Details

### Cache Structure
```python
_openai_client_cache: dict[tuple[float, int], OpenAI] = {}
```
- **Key**: `(timeout, max_retries)` tuple
- **Value**: OpenAI client instance

### How It Works
1. When `get_openai_client()` is called, it reads timeout and max_retries from environment variables
2. Creates a cache key from these values: `(timeout, max_retries)`
3. Checks if a client with this configuration already exists in the cache
4. If yes: returns the cached client (logs DEBUG message)
5. If no: creates a new client, caches it, and returns it (logs INFO message)

### Code Changes
**File**: `src/config.py`

**Changes**:
- Added `_openai_client_cache` dictionary
- Modified `get_openai_client()` to implement caching logic
- Added comprehensive docstring
- Added logging for client creation and reuse

## Benefits

### Performance
- **Connection Pooling**: Reuses httpx connection pools within each client
- **Reduced Overhead**: No need to create new client instances unnecessarily
- **Faster Requests**: Connection reuse reduces handshake time

### Stability
- **Fewer Connections**: Reduces total number of TCP connections
- **Connection Errors**: Less likely to hit connection limits
- **Resource Efficiency**: Lower memory and CPU usage

### Compatibility
- **Backward Compatible**: No changes needed to existing code
- **Configuration Aware**: Different timeout/retry settings still create separate clients
- **Thread-Safe**: httpx connection pools are thread-safe

## Testing

### Test Coverage
**File**: `src/tests/test_singleton_openai_client.py`

**Tests**:
1. `test_openai_client_singleton()`: Verifies same configuration returns same instance
2. `test_openai_client_different_configs()`: Verifies different configurations create different instances
3. `test_openai_client_cache_key()`: Verifies cache key structure

All tests pass successfully ✅

### Existing Tests
- All existing tests continue to pass
- `test_logfire_integration.py` passes without modifications
- No breaking changes to existing functionality

## Usage Examples

### Basic Usage
```python
from src import config

# Get default client (uses environment variables)
client, model = config.get_openai_client()

# Get client with specific model name
client, model = config.get_openai_client("gpt-4")

# Both calls return the same client instance if timeout/max_retries are the same
```

### With Different Configurations
```python
import os
from src import config

# Configuration 1: Default (300s timeout, 3 retries)
os.environ["OPENAI_TIMEOUT"] = "300"
os.environ["OPENAI_MAX_RETRIES"] = "3"
client1, _ = config.get_openai_client()

# Configuration 2: Longer timeout (600s timeout, 5 retries)
os.environ["OPENAI_TIMEOUT"] = "600"
os.environ["OPENAI_MAX_RETRIES"] = "5"
client2, _ = config.get_openai_client()

# client1 and client2 are different instances
assert client1 is not client2

# Back to Configuration 1 - reuses client1
os.environ["OPENAI_TIMEOUT"] = "300"
os.environ["OPENAI_MAX_RETRIES"] = "3"
client3, _ = config.get_openai_client()

# client3 is the same as client1
assert client3 is client1
```

## Environment Variables

### Required
- `OPENAI_API_KEY`: OpenAI API key

### Optional (affect caching)
- `OPENAI_TIMEOUT`: Request timeout in seconds (default: 300)
- `OPENAI_MAX_RETRIES`: Maximum retry attempts (default: 3)

Note: Different values for timeout or max_retries will create separate cached client instances.

## Monitoring

### Logging
- **INFO level**: New client creation
  - Example: `Creating new OpenAI client with timeout=300.0, max_retries=3`
- **DEBUG level**: Cached client reuse
  - Example: `Reusing cached OpenAI client with timeout=300.0, max_retries=3`

### Cache Inspection
```python
from src import config

# Check number of cached clients
print(f"Cached clients: {len(config._openai_client_cache)}")

# Check cache keys (configurations)
print(f"Cache keys: {list(config._openai_client_cache.keys())}")
```

## Future Considerations

### Thread Safety
The current implementation is thread-safe because:
- Dictionary operations are atomic in Python
- httpx client pools are thread-safe
- No complex state mutations

### Memory Management
- Cached clients persist for the lifetime of the application
- In practice, few different configurations are used (typically 1-2)
- Memory footprint is negligible

### Potential Enhancements
1. Add ability to clear cache if needed
2. Add metrics for cache hit/miss rates
3. Consider TTL (time-to-live) for cached clients if needed
4. Add cache size limits if many configurations are expected

## Related Files
- `src/config.py`: Implementation
- `src/tests/test_singleton_openai_client.py`: Tests
- `src/tests/test_logfire_integration.py`: Integration tests

## References
- OpenAI Python SDK: https://github.com/openai/openai-python
- httpx documentation: https://www.python-httpx.org/
- Issue: "Use a singleton for OpenAI client to leverage httpx optimisation and avoid connection errors"
