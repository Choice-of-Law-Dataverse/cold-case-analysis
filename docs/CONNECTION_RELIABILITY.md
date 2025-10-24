# OpenAI API Connection Reliability

This document explains how to configure the CoLD Case Analyzer to prevent and handle OpenAI API connection errors.

## Configuration Parameters

The application supports the following environment variables to improve connection reliability:

### `OPENAI_TIMEOUT`

**Default:** `300` (seconds / 5 minutes)

Controls how long the application will wait for an API response before timing out.

**When to increase:**
- You have a slow or unreliable network connection
- You're experiencing frequent timeout errors
- You're analyzing very large court decisions that take longer to process

**Example:**
```bash
OPENAI_TIMEOUT="180"  # 3 minutes
```

### `OPENAI_MAX_RETRIES`

**Default:** `3`

Controls how many times the application will automatically retry a failed API request before giving up.

**When to increase:**
- You experience frequent transient network issues (e.g., intermittent Wi-Fi)
- You're on a network with occasional packet loss
- You want the system to be more resilient to temporary API outages

**When to decrease:**
- You want faster failure detection
- You're debugging connection issues and don't want automatic retries masking problems

**Example:**
```bash
OPENAI_MAX_RETRIES="5"  # Retry up to 5 times
```

## Setting Environment Variables

### Using .env file (Recommended)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add or modify the connection parameters:
   ```bash
   # OpenAI API Connection Settings
   OPENAI_TIMEOUT="180"
   OPENAI_MAX_RETRIES="5"
   ```

3. Restart the application to apply changes

### Using Docker

If running with Docker, add these to your `docker-compose.yml` or pass them as environment variables:

```yaml
environment:
  - OPENAI_TIMEOUT=180
  - OPENAI_MAX_RETRIES=5
```

### Using Streamlit Cloud

Add these to your Streamlit Cloud secrets:

```toml
[env]
OPENAI_TIMEOUT = "180"
OPENAI_MAX_RETRIES = "5"
```

## Error Handling

The application handles OpenAI API errors gracefully:

### Connection Errors
**Error:** Unable to connect to OpenAI servers
**User Message:** "Unable to connect to the AI service. Please check your internet connection and try again."
**What to do:**
- Check your internet connection
- Verify firewall/proxy settings
- Increase `OPENAI_MAX_RETRIES` for automatic retry

### Timeout Errors
**Error:** Request takes too long to complete
**User Message:** "The AI service request timed out. Please try again in a moment."
**What to do:**
- Increase `OPENAI_TIMEOUT` to allow more time
- Try analyzing a smaller document
- Check if the OpenAI API is experiencing issues

### Rate Limit Errors
**Error:** Too many requests sent too quickly
**User Message:** "Too many requests to the AI service. Please wait a moment and try again."
**What to do:**
- Wait a few seconds before retrying
- The application will automatically retry with exponential backoff

### Authentication Errors
**Error:** Invalid or missing API key
**User Message:** "Authentication failed with the AI service. Please check your API key configuration."
**What to do:**
- Verify your `OPENAI_API_KEY` is set correctly in `.env`
- Check that your API key is valid and has sufficient credits
- Ensure the API key hasn't expired

## Best Practices

1. **Start with defaults:** The default values (300s timeout, 3 retries) work well for most scenarios

2. **Increase timeout for large documents:** If analyzing very long court decisions (>50 pages), consider increasing timeout to 360-480 seconds

3. **Increase retries for unreliable networks:** If on mobile or Wi-Fi with intermittent connectivity, set `OPENAI_MAX_RETRIES` to 5 or higher

4. **Monitor logs:** Check application logs (INFO level) to see when retries occur and adjust accordingly

5. **Balance resilience vs speed:** Higher retries make the system more resilient but can make failures take longer to detect

## Example Configurations

### Slow Network / Large Documents
```bash
OPENAI_TIMEOUT="240"      # 4 minutes
OPENAI_MAX_RETRIES="5"    # More retry attempts
```

### Fast Network / Quick Failure Detection
```bash
OPENAI_TIMEOUT="60"       # 1 minute
OPENAI_MAX_RETRIES="2"    # Fewer retries
```

### Maximum Resilience (Development/Testing)
```bash
OPENAI_TIMEOUT="300"      # 5 minutes
OPENAI_MAX_RETRIES="10"   # Many retry attempts
```

### Production (Balanced)
```bash
OPENAI_TIMEOUT="300"      # 5 minutes (default)
OPENAI_MAX_RETRIES="3"    # Standard retries (default)
```

## Troubleshooting

### Issue: Frequent timeout errors
**Solution:** Increase `OPENAI_TIMEOUT` to 180 or 240 seconds

### Issue: Connection drops during analysis
**Solution:** Increase `OPENAI_MAX_RETRIES` to 5 or more

### Issue: Analysis takes too long to fail
**Solution:** Decrease `OPENAI_TIMEOUT` to 60 seconds

### Issue: Getting rate limit errors
**Solution:** This is expected with heavy usage. The application handles these automatically with retries. If persistent, you may need to upgrade your OpenAI plan.

## Technical Details

The timeout and retry settings are applied to both:
- **LangChain ChatOpenAI client** (used for some operations)
- **OpenAI SDK client** (used for agent-based operations)

Both clients use the same timeout and retry configuration for consistency.

### Retry Behavior

When a request fails, the OpenAI SDK automatically:
1. Waits for an exponentially increasing duration (e.g., 1s, 2s, 4s, 8s)
2. Retries the request up to `OPENAI_MAX_RETRIES` times
3. Returns an error if all retries are exhausted

This exponential backoff helps avoid overwhelming the API during temporary outages.
