import json
import logging
import os
import uuid

import logfire
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import OpenAI

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
_openai_client_cache: dict[tuple[float, int], OpenAI] = {}


def get_openai_client(model: str | None = None):
    """
    Return an OpenAI client instance with the specified model.
    Uses a singleton pattern to reuse client instances and leverage httpx connection pooling.
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


# default llm instance (legacy)
llm = get_llm()

# default OpenAI client
openai_client, default_model = get_openai_client()

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
