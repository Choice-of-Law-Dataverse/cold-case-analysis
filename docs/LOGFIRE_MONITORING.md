# Logfire Monitoring and Instrumentation

The CoLD Case Analyzer uses [Logfire](https://logfire.pydantic.dev/) for monitoring and observability, with special focus on tracking LLM calls and performance metrics.

## Overview

Logfire provides:
- **Automatic LLM call tracing**: All OpenAI/LangChain API calls are automatically instrumented
- **Custom spans**: Key analysis operations are wrapped in spans for detailed performance tracking
- **Distributed tracing**: Track requests across the entire analysis pipeline
- **Performance metrics**: Monitor execution time, token usage, and model performance

## Setup

### 1. Get a Logfire Token

1. Sign up at [Logfire](https://logfire.pydantic.dev/)
2. Create a project
3. Copy your project token

### 2. Configure the Application

Add your Logfire token to the `.env` file:

```bash
# Optional - Enable Logfire monitoring
LOGFIRE_TOKEN="your_logfire_token_here"
```

**Note**: The token is optional. If not provided:
- Instrumentation will still be active (no errors)
- Spans and traces will be generated locally
- No data will be sent to Logfire (local-only mode)

### 3. Verify Setup

Run the application and check the logs:

```bash
streamlit run src/app.py
```

You should see log messages like:
```
INFO - Logfire monitoring initialized with token
INFO - OpenAI instrumentation enabled
```

## What Gets Traced

### Automatic Instrumentation

**OpenAI/LangChain calls** are automatically traced with:
- Request/response details
- Model name and parameters
- Token counts and costs
- Execution time
- Error tracking

### Custom Spans

The following analysis operations have custom spans:

1. **Jurisdiction Detection** (`detect_legal_system_type`)
   - Jurisdiction name
   - Detection method (mapping vs LLM)
   - Classification result

2. **CoL Section Extraction** (`extract_col_section`)
   - Extraction iteration count
   - Response length
   - Execution time

3. **Theme Classification** (`classify_themes`)
   - Classified themes
   - Number of themes
   - Retry attempts
   - Validation time

4. **Analysis Operations**:
   - `extract_relevant_facts` - Factual background extraction
   - `extract_pil_provisions` - Legal provisions identification
   - `extract_col_issue` - Choice of Law issue analysis
   - `generate_abstract` - Final abstract generation

Each span includes:
- Operation name
- Input/output sizes
- Execution time
- Relevant metadata

## Viewing Traces

### In Logfire Dashboard

1. Log into [Logfire](https://logfire.pydantic.dev/)
2. Navigate to your project
3. View traces in the dashboard

You'll see:
- Request timeline
- Span hierarchy
- LLM call details
- Performance metrics
- Error tracking

### Example Trace Structure

```
case_analysis [root span]
├── detect_legal_system_type
│   └── openai.chat.completions.create
├── extract_col_section
│   └── openai.chat.completions.create
├── classify_themes
│   ├── openai.chat.completions.create [attempt 1]
│   └── openai.chat.completions.create [attempt 2]
└── analysis_workflow
    ├── extract_relevant_facts
    │   └── openai.chat.completions.create
    ├── extract_pil_provisions
    │   └── openai.chat.completions.create
    ├── extract_col_issue
    │   └── openai.chat.completions.create
    └── generate_abstract
        └── openai.chat.completions.create
```

## Performance Monitoring

### Key Metrics to Track

1. **LLM Response Times**
   - Average response time per model
   - P95/P99 latencies
   - Outlier detection

2. **Token Usage**
   - Input/output token counts
   - Cost per analysis
   - Model efficiency

3. **Analysis Quality**
   - Retry counts (theme classification)
   - Iteration counts (CoL extraction)
   - User feedback scores

4. **Error Rates**
   - Failed LLM calls
   - Parsing errors
   - Timeout issues

## Local Development

For local development without sending data to Logfire:

```python
# config.py automatically handles this
if not logfire_token:
    logfire.configure(send_to_logfire=False)
    # Instrumentation active, no data sent
```

All spans and traces are still generated for local debugging, but no data leaves your machine.

## Integration with Existing Logging

Logfire works alongside the existing Python logging:

- **Python `logging`**: Detailed debug logs, error messages
- **Logfire spans**: High-level operation tracking, performance metrics
- **OpenTelemetry**: Automatic LLM call instrumentation

All three work together without conflicts.

## Distributed Tracing

For multi-service deployments, Logfire automatically propagates trace context:

```python
# Trace IDs are automatically propagated across:
# - HTTP requests
# - LLM calls
# - Database queries
# - External API calls
```

See [Logfire Distributed Tracing Guide](https://logfire.pydantic.dev/docs/how-to-guides/distributed-tracing/) for more details.

## Environments

For production deployments, configure different environments:

```bash
# Development
LOGFIRE_ENVIRONMENT="development"

# Staging
LOGFIRE_ENVIRONMENT="staging"

# Production
LOGFIRE_ENVIRONMENT="production"
```

See [Logfire Environments Guide](https://logfire.pydantic.dev/docs/how-to-guides/environments/) for configuration details.

## Best Practices

1. **Use descriptive span names**: Custom spans use operation names like `extract_col_section`
2. **Add relevant attributes**: Include metadata like iteration count, text length, etc.
3. **Log important events**: Use `logfire.info()` for significant milestones
4. **Monitor token usage**: Track costs across different models
5. **Set up alerts**: Configure alerts for high latency or error rates

## Troubleshooting

### "Logfire API is unreachable" Warning

This is normal in environments without internet access to `logfire-us.pydantic.dev`. The application continues to work normally with local-only instrumentation.

### No Traces Appearing

1. Check that `LOGFIRE_TOKEN` is set correctly
2. Verify internet connectivity to Logfire API
3. Check Logfire project permissions
4. Review application logs for errors

### Performance Impact

Logfire instrumentation has minimal overhead:
- ~1-2ms per span
- Async data sending (non-blocking)
- Automatic batching and sampling

## Resources

- [Logfire Documentation](https://logfire.pydantic.dev/docs/)
- [OpenAI Integration](https://logfire.pydantic.dev/docs/integrations/llms/openai/)
- [LangChain Integration](https://logfire.pydantic.dev/docs/integrations/llms/langchain/)
- [Distributed Tracing](https://logfire.pydantic.dev/docs/how-to-guides/distributed-tracing/)
- [Environment Configuration](https://logfire.pydantic.dev/docs/how-to-guides/environments/)
