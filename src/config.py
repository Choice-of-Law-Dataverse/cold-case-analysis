import json
import logging
import os
import uuid

import logfire
from agents import Agent, Runner
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


def get_llm(model: str | None = None):
    """
    Return a ChatOpenAI instance. If `model` is provided, use it; otherwise fallback to env var or default.
    """
    selected = model or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
    return ChatOpenAI(model=selected)


def get_openai_client(model: str | None = None):
    """
    Return an OpenAI client instance with the specified model.
    """
    selected = model or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
    return OpenAI(), selected


def create_agent(name: str, instructions: str, output_type: type, model: str | None = None):
    """
    Create an OpenAI Agent with structured output.

    Args:
        name: Name of the agent
        instructions: System instructions for the agent
        output_type: Pydantic model for structured output
        model: Optional model override

    Returns:
        Agent instance configured for structured output
    """
    selected_model = model or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
    return Agent(
        name=name,
        instructions=instructions,
        output_type=output_type,
        model=selected_model,
    )


def run_agent(agent: Agent, prompt: str):
    """
    Run an agent with the given prompt and return the structured output.

    Args:
        agent: Agent instance
        prompt: User prompt

    Returns:
        Parsed output from the agent
    """
    result = Runner.run(agent, prompt)
    return result.final_output


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
