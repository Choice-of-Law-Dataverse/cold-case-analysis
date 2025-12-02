import json
import logging
import os
import uuid

import logfire
import nest_asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# Apply nest_asyncio to allow asyncio.run() in Streamlit's event loop
# This is necessary because Streamlit uses Tornado's event loop, which conflicts with asyncio.run()
# See: https://github.com/openai/openai-agents-python/issues/77
nest_asyncio.apply()

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


def get_openai_client():
    """
    Return an AsyncOpenAI client instance for use with openai-agents library.
    """
    timeout = float(os.getenv("OPENAI_TIMEOUT", "300"))
    max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "3"))

    # Always create a new client to ensure thread-safety across event loops
    # logger.debug("Creating new AsyncOpenAI client for thread/loop safety")
    client = AsyncOpenAI(timeout=timeout, max_retries=max_retries)

    return client


# Configuration for Model Routing
# Maps analysis steps to specific models to optimize for cost and quality
# gpt-5-nano: Fast, cheap, good for classification and simple extraction
# gpt-5-mini: Balanced, good for summarization and text generation
# gpt-5.1: High reasoning capability, best for complex legal analysis
TASK_MODELS = {
    "abstract": "gpt-5-mini",
    "case_citation": "gpt-5-nano",
    "col_issue": "gpt-5.1",
    "col_section": "gpt-5-mini",
    "courts_position": "gpt-5.1",
    "dissenting_opinions": "gpt-5.1",
    "jurisdiction_classification": "gpt-5-nano",
    "legal_system": "gpt-5-nano",
    "obiter_dicta": "gpt-5.1",
    "pil_provisions": "gpt-5-nano",
    "relevant_facts": "gpt-5-mini",
    "themes": "gpt-5-nano",
}


def get_model(task: str) -> str:
    """
    Get the appropriate model for a specific task.
    """

    return TASK_MODELS.get(task, "gpt-5-nano")


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
