import json
import logging
import os
import uuid

import agents
import logfire
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI, OpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")

# Initialize Logfire for monitoring and instrumentation
# Token is optional - if not provided, Logfire will not send data but instrumentation will still work
logfire_token = os.getenv("LOGFIRE_TOKEN")
if logfire_token:
    logfire.configure(token=logfire_token)
    logger.info("Logfire monitoring initialized with token")
else:
    logfire.configure(send_to_logfire=False)
    logger.info("Logfire instrumentation enabled (local only - no token provided)")

# Instrument OpenAI/LangChain calls for automatic tracing
logfire.instrument_openai()
logfire.instrument_openai_agents()
logger.info("OpenAI instrumentation enabled")

# Instrument requests library for tracing HTTP calls
logfire.instrument_requests()

# Instrument psycopg2 if using PostgreSQL for tracing DB calls
logfire.instrument_psycopg()


def get_llm(model: str | None = None):
    """
    Return a ChatOpenAI instance. If `model` is provided, use it; otherwise fallback to env var or default.
    """
    selected = model or os.getenv("OPENAI_MODEL") or "gpt-5-nano"

    # Get timeout and retry settings from environment
    # OpenAI SDK expects float for timeout
    timeout = float(os.getenv("OPENAI_TIMEOUT", "300"))
    max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "3"))

    return ChatOpenAI(
        model=selected,
        timeout=timeout,
        max_retries=max_retries
    )


# Singleton cache for OpenAI clients
# Key is (timeout, max_retries) to support different configurations
# This enables connection pooling and reuse while respecting different timeout/retry requirements
_openai_client_cache: dict[tuple[float, int], OpenAI] = {}
_async_openai_client_cache: dict[tuple[float, int], AsyncOpenAI] = {}


def get_openai_client(model: str | None = None):
    """
    Return an OpenAI client instance with the specified model.
    Uses a singleton pattern to reuse client instances and leverage httpx connection pooling.

    The client is cached based on its configuration (timeout, max_retries) to ensure
    that different configurations get separate client instances while allowing reuse
    of clients with the same configuration. This approach:

    - Leverages httpx connection pooling for better performance
    - Reduces the number of TCP connections to OpenAI's API
    - Prevents connection errors from too many simultaneous connections
    - Maintains thread-safe httpx connection pools within each client

    Args:
        model: Optional model name. If not provided, uses OPENAI_MODEL env var or defaults to "gpt-5-nano".
               Note: The model parameter only affects the returned model name, not the cached client instance.

    Returns:
        A tuple of (OpenAI client instance, selected model name)

    Environment Variables:
        OPENAI_API_KEY: Required - OpenAI API key
        OPENAI_TIMEOUT: Optional - Request timeout in seconds (default: 300)
        OPENAI_MAX_RETRIES: Optional - Maximum retry attempts (default: 3)
    """
    selected = model or os.getenv("OPENAI_MODEL") or "gpt-5-nano"

    # Get timeout and retry settings from environment
    # OpenAI SDK expects float for timeout
    timeout = float(os.getenv("OPENAI_TIMEOUT", "300"))
    max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "3"))

    # Create cache key based on configuration
    cache_key = (timeout, max_retries)

    # Return cached client if it exists with the same configuration
    if cache_key in _openai_client_cache:
        logger.debug("Reusing cached OpenAI client with timeout=%s, max_retries=%s", timeout, max_retries)
        return _openai_client_cache[cache_key], selected

    # Create new client and cache it
    logger.info("Creating new OpenAI client with timeout=%s, max_retries=%s", timeout, max_retries)
    client = OpenAI(
        timeout=timeout,
        max_retries=max_retries
    )
    _openai_client_cache[cache_key] = client

    return client, selected


def get_async_openai_client(model: str | None = None):
    """
    Return an AsyncOpenAI client instance for use with openai-agents library.
    Uses a singleton pattern to reuse client instances and leverage httpx connection pooling.

    The client is cached based on its configuration (timeout, max_retries) to ensure
    that different configurations get separate client instances while allowing reuse
    of clients with the same configuration.

    Args:
        model: Optional model name. If not provided, uses OPENAI_MODEL env var or defaults to "gpt-5-nano".
               Note: The model parameter only affects the returned model name, not the cached client instance.

    Returns:
        A tuple of (AsyncOpenAI client instance, selected model name)

    Environment Variables:
        OPENAI_API_KEY: Required - OpenAI API key
        OPENAI_TIMEOUT: Optional - Request timeout in seconds (default: 300)
        OPENAI_MAX_RETRIES: Optional - Maximum retry attempts (default: 3)
    """
    selected = model or os.getenv("OPENAI_MODEL") or "gpt-5-nano"

    timeout = float(os.getenv("OPENAI_TIMEOUT", "300"))
    max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "3"))

    cache_key = (timeout, max_retries)

    if cache_key in _async_openai_client_cache:
        logger.debug("Reusing cached AsyncOpenAI client with timeout=%s, max_retries=%s", timeout, max_retries)
        return _async_openai_client_cache[cache_key], selected

    logger.info("Creating new AsyncOpenAI client with timeout=%s, max_retries=%s", timeout, max_retries)
    client = AsyncOpenAI(
        timeout=timeout,
        max_retries=max_retries
    )
    _async_openai_client_cache[cache_key] = client

    return client, selected


# default llm instance (legacy)
llm = get_llm()

# default OpenAI client
openai_client, default_model = get_openai_client()

# Configure openai-agents to use our AsyncOpenAI client with retry settings
# This ensures all Agent instances use the configured retry mechanism from the OpenAI SDK
async_openai_client, _ = get_async_openai_client()
agents.set_default_openai_client(async_openai_client)
logger.info("Configured openai-agents to use AsyncOpenAI client with retry settings")

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_CONCEPTS_TABLE = os.getenv("AIRTABLE_CONCEPTS_TABLE")

NOCODB_BASE_URL = os.getenv("NOCODB_BASE_URL")
NOCODB_API_TOKEN = os.getenv("NOCODB_API_TOKEN")
NOCODB_POSTGRES_SCHEMA = os.getenv("NOCODB_POSTGRES_SCHEMA")

SQL_CONN_STRING = os.getenv("SQL_CONN_STRING")
# Load user credentials (as JSON string in .env): e.g. USER_CREDENTIALS='{"alice":"wonderland","bob":"builder"}'
USER_CREDENTIALS = json.loads(os.getenv("USER_CREDENTIALS", "{}"))

thread_id = str(uuid.uuid4())
