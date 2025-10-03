import json
import os
import uuid

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")

def get_llm(model: str | None = None):
    """
    Return a ChatOpenAI instance. If `model` is provided, use it; otherwise fallback to env var or default.
    """
    selected = model or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
    return ChatOpenAI(model=selected)

# default llm instance
llm = get_llm()

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
#print(f"Thread ID: {thread_id}")
