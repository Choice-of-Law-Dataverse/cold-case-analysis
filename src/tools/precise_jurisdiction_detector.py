# tools/precise_jurisdiction_detector.py
"""
Identifies the precise jurisdiction from court decision text using the jurisdictions.csv database.
"""

import csv
import re
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

import config
from prompts.precise_jurisdiction_detection_prompt import PRECISE_JURISDICTION_DETECTION_PROMPT

from .jurisdiction_detector import (
    detect_legal_system_by_jurisdiction,
    detect_legal_system_type,
)


def _coerce_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(item) for item in content if item is not None)
    return str(content) if content is not None else ""


def determine_legal_system_type(jurisdiction_name: str, text: str | None = None) -> str:
    if text is not None:
        return detect_legal_system_type(jurisdiction_name, text)
    fallback = detect_legal_system_by_jurisdiction(jurisdiction_name)
    return fallback or "No court decision"


def load_jurisdictions():
    """Load all jurisdictions from the CSV file."""
    jurisdictions_file = Path(__file__).parent.parent / "data" / "jurisdictions.csv"
    jurisdictions = []

    with open(jurisdictions_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Name"].strip():  # Only include rows with actual jurisdiction names
                jurisdictions.append(
                    {
                        "name": row["Name"].strip(),
                        "code": row["Alpha-3 Code"].strip(),
                        "summary": row["Jurisdiction Summary"].strip(),
                    }
                )
    # Sort jurisdictions by name for better consistency
    jurisdictions.sort(key=lambda x: x["name"].lower())
    return jurisdictions


def create_jurisdiction_list():
    """Create a formatted list of jurisdictions for the LLM prompt."""
    jurisdictions = load_jurisdictions()
    jurisdiction_list = []

    for jurisdiction in jurisdictions:
        jurisdiction_list.append(f"- {jurisdiction['name']}")

    return "\n".join(jurisdiction_list)


def detect_precise_jurisdiction(text: str) -> str:
    """
    Uses an LLM to identify the precise jurisdiction from court decision text.
    Returns the jurisdiction name as a string in the format "Jurisdiction".
    """
    if not text or len(text.strip()) < 50:
        return "Unknown"

    jurisdiction_list = create_jurisdiction_list()

    prompt = PRECISE_JURISDICTION_DETECTION_PROMPT.format(
        jurisdiction_list=jurisdiction_list,
        text=text[:5000],  # Limit text length to avoid token limits
    )
    print(f"\nPrompting LLM with:\n{prompt}\n")

    try:
        response = config.llm.invoke(
            [
                SystemMessage(
                    content="You are an expert in legal systems and court jurisdictions worldwide. Follow the format exactly as requested."
                ),
                HumanMessage(content=prompt),
            ]
        )

        result_text = _coerce_to_text(getattr(response, "content", "")).strip()
        print(f"\nLLM Response: {result_text}\n")

        # Extract jurisdiction from the /"Jurisdiction"/ format
        # Look for text between /" and "/
        jurisdiction_match = re.search(r"/\"([^\"]+)\"/", result_text)
        if jurisdiction_match:
            jurisdiction_name = jurisdiction_match.group(1)
        else:
            # Fallback: try to extract any quoted jurisdiction name
            quote_match = re.search(r"\"([^\"]+)\"", result_text)
            if quote_match:
                jurisdiction_name = quote_match.group(1)
            else:
                # Final fallback: use the entire response if it's reasonable
                if len(result_text) < 100 and result_text not in ["Unknown", "unknown"]:
                    jurisdiction_name = result_text.strip()
                else:
                    jurisdiction_name = "Unknown"

        # Validate jurisdiction against our list
        jurisdictions = load_jurisdictions()

        if jurisdiction_name and jurisdiction_name != "Unknown":
            # First try exact match
            for jurisdiction in jurisdictions:
                if jurisdiction["name"].lower() == jurisdiction_name.lower():
                    return jurisdiction["name"]

            # Then try partial match (contains)
            for jurisdiction in jurisdictions:
                if (
                    jurisdiction_name.lower() in jurisdiction["name"].lower()
                    or jurisdiction["name"].lower() in jurisdiction_name.lower()
                ):
                    return jurisdiction["name"]

            # If no match found but we have a reasonable response, return it
            if len(jurisdiction_name) > 2 and jurisdiction_name not in ["Unknown", "unknown", "N/A", "None"]:
                return jurisdiction_name

        return "Unknown"

    except Exception as e:
        print(f"Error in jurisdiction detection: {e}")
        return "Unknown"
