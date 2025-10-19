# Logfire Instrumentation Documentation

This document describes the comprehensive logfire monitoring instrumentation implemented in the CoLD Case Analysis application.

## Overview

The application uses [Logfire](https://logfire.pydantic.dev/) for observability and monitoring. Logfire provides automatic tracing of API calls, database operations, and custom span instrumentation for key application functions.

## Configuration

Logfire is configured in `src/config.py`:

```python
import logfire

# Initialize Logfire (token optional - works locally without it)
logfire_token = os.getenv("LOGFIRE_TOKEN")
if logfire_token:
    logfire.configure(token=logfire_token)
else:
    logfire.configure(send_to_logfire=False)

# Automatic instrumentation
logfire.instrument_openai()          # OpenAI/LangChain API calls
logfire.instrument_openai_agents()   # OpenAI Agents framework
logfire.instrument_requests()        # HTTP requests via requests library
logfire.instrument_psycopg()         # PostgreSQL database calls
```

## Automatic Instrumentation

These components are automatically instrumented and require no code changes:

### 1. OpenAI API Calls
- **What**: All LLM API calls via OpenAI SDK and LangChain
- **Instrumentation**: `logfire.instrument_openai()` and `logfire.instrument_openai_agents()`
- **Traces**: Request/response payloads, token usage, latency, errors

### 2. HTTP Requests
- **What**: All HTTP requests via the `requests` library
- **Instrumentation**: `logfire.instrument_requests()`
- **Traces**: URL, method, status code, headers, latency, errors

### 3. Database Operations
- **What**: All PostgreSQL queries via psycopg2
- **Instrumentation**: `logfire.instrument_psycopg()`
- **Traces**: SQL queries, parameters, execution time, errors

## Manual Span Instrumentation

The following functions have explicit logfire spans for detailed monitoring:

### Workflow Orchestration

#### `analyze_case_workflow`
- **File**: `src/tools/case_analyzer.py`
- **Span**: `analyze_case_workflow`
- **Purpose**: Main workflow that orchestrates all analysis steps
- **Includes**: Parallel execution tracking, step completion events

### Jurisdiction Detection

#### `detect_legal_system_type`
- **File**: `src/tools/jurisdiction_detector.py`
- **Span**: `detect_legal_system_type`
- **Purpose**: Detects if court decision is Civil Law, Common Law, or not a court decision
- **Metadata**: Includes jurisdiction name in span attributes

#### `detect_precise_jurisdiction`
- **File**: `src/tools/jurisdiction_classifier.py`
- **Span**: `detect_precise_jurisdiction`
- **Purpose**: Identifies the precise jurisdiction from court decision text
- **Function**: `detect_precise_jurisdiction_with_confidence()`

### Extraction Functions

#### `extract_col_section`
- **File**: `src/tools/col_extractor.py`
- **Span**: `extract_col_section`
- **Purpose**: Extracts Choice of Law sections from court decision

#### `extract_case_citation`
- **File**: `src/tools/case_citation_extractor.py`
- **Span**: `extract_case_citation`
- **Purpose**: Extracts case citation information

#### `extract_col_issue`
- **File**: `src/tools/col_issue_extractor.py`
- **Span**: `extract_col_issue`
- **Purpose**: Extracts Choice of Law issue from decision

#### `extract_relevant_facts`
- **File**: `src/tools/relevant_facts_extractor.py`
- **Span**: `extract_relevant_facts`
- **Purpose**: Extracts relevant facts from court decision

#### `extract_pil_provisions`
- **File**: `src/tools/pil_provisions_extractor.py`
- **Span**: `extract_pil_provisions`
- **Purpose**: Extracts Private International Law provisions

#### `extract_courts_position`
- **File**: `src/tools/courts_position_extractor.py`
- **Span**: `extract_courts_position`
- **Purpose**: Extracts the court's position on the PIL issue

#### `extract_obiter_dicta`
- **File**: `src/tools/obiter_dicta_extractor.py`
- **Span**: `extract_obiter_dicta`
- **Purpose**: Extracts obiter dicta (Common Law jurisdictions only)

#### `extract_dissenting_opinions`
- **File**: `src/tools/dissenting_opinions_extractor.py`
- **Span**: `extract_dissenting_opinions`
- **Purpose**: Extracts dissenting opinions (Common Law jurisdictions only)

### Classification

#### `classify_themes`
- **File**: `src/tools/theme_classifier.py`
- **Span**: `classify_themes`
- **Purpose**: Classifies legal themes for the court decision

### Generation

#### `generate_abstract`
- **File**: `src/tools/abstract_generator.py`
- **Span**: `generate_abstract`
- **Purpose**: Generates final abstract from all extracted information

### Database Operations

#### `save_to_db`
- **File**: `src/components/database.py`
- **Span**: `save_to_db`
- **Purpose**: Persists analysis state to PostgreSQL database

## Span Naming Convention

All manual spans follow a consistent naming convention:
- **Format**: Snake case (`snake_case`)
- **Pattern**: Matches the function name exactly
- **Rationale**: Easy correlation between spans and code, consistent with Python naming conventions

## Usage Examples

### Viewing Traces Locally

When running without a `LOGFIRE_TOKEN`, spans are still created and logged locally:

```bash
# Run the application
streamlit run src/app.py

# Spans will appear in console logs with timestamps
# Example: 13:20:49.555 detect_legal_system_type jurisdiction="Switzerland"
```

### Viewing Traces in Logfire Dashboard

When running with a `LOGFIRE_TOKEN`:

```bash
# Set token in .env file
LOGFIRE_TOKEN=your_token_here

# Run the application
streamlit run src/app.py

# View traces at https://logfire.pydantic.dev/
```

### Adding New Spans

To add a span to a new function:

```python
import logfire

def my_new_function():
    with logfire.span("my_new_function"):
        # Your function logic here
        pass
```

To add span with attributes:

```python
import logfire

def my_function_with_metadata(user_id: str):
    with logfire.span("my_function", user_id=user_id):
        # Your function logic here
        pass
```

## Testing

Logfire instrumentation is tested in `src/tests/test_logfire_integration.py`:

```bash
# Run tests
python src/tests/test_logfire_integration.py

# Expected output:
# ✓ test_logfire_is_configured
# ✓ test_logfire_instrumentation_without_token
# ✓ test_openai_instrumentation_enabled
# ✓ test_llm_calls_are_instrumented
# ✓ test_jurisdiction_classifier_has_span
# ✓ test_database_save_has_span
```

## Benefits

1. **Automatic Tracing**: LLM calls, HTTP requests, and database queries are automatically traced
2. **Performance Monitoring**: Identify slow operations and bottlenecks
3. **Error Tracking**: Automatic capture of exceptions and error contexts
4. **Request Flow**: Visualize complete request flow through the system
5. **Cost Tracking**: Monitor LLM token usage and costs
6. **No Code Changes Needed**: Most instrumentation is automatic via decorators

## Troubleshooting

### Spans Not Appearing

If spans aren't showing up in Logfire:

1. Check that `LOGFIRE_TOKEN` is set correctly
2. Verify network connectivity to logfire-us.pydantic.dev
3. Check logs for configuration warnings

### Local Development

For local development without sending data to Logfire:

```bash
# Don't set LOGFIRE_TOKEN or set it to empty
LOGFIRE_TOKEN=

# Spans will be created and logged locally but not sent to cloud
```

## References

- [Logfire Documentation](https://logfire.pydantic.dev/)
- [OpenAI Instrumentation](https://logfire.pydantic.dev/docs/integrations/openai/)
- [Database Instrumentation](https://logfire.pydantic.dev/docs/integrations/psycopg/)
- [Requests Instrumentation](https://logfire.pydantic.dev/docs/integrations/requests/)
