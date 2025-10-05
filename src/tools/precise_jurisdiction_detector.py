# tools/precise_jurisdiction_detector.py
"""
Identifies the precise jurisdiction from court decision text using the jurisdictions.csv database.
"""

import asyncio
import csv
import logging
import os
from pathlib import Path
from typing import Any

from agents import Agent, Runner

from models.classification_models import JurisdictionOutput
from prompts.precise_jurisdiction_detection_prompt import PRECISE_JURISDICTION_DETECTION_PROMPT

from .jurisdiction_detector import (
    detect_legal_system_by_jurisdiction,
    detect_legal_system_type,
)

logger = logging.getLogger(__name__)


def _run_agent_sync(agent: Agent, prompt: str):
    """Helper function to run an agent synchronously in Streamlit context."""

    async def run_agent_async():
        result = await Runner.run(agent, prompt)
        return result.final_output

    return asyncio.run(run_agent_async())


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

    This is the legacy interface - calls detect_precise_jurisdiction_with_confidence internally.
    """
    result = detect_precise_jurisdiction_with_confidence(text)
    return result["jurisdiction_name"]


def detect_precise_jurisdiction_with_confidence(text: str, model: str | None = None) -> dict:
    """
    Uses an LLM to identify the precise jurisdiction from court decision text with confidence.
    Returns a dict with jurisdiction data including confidence and reasoning.
    """
    if not text or len(text.strip()) < 50:
        return {
            "jurisdiction_name": "Unknown",
            "legal_system_type": "Unknown",
            "jurisdiction_code": "UNK",
            "confidence": "low",
            "reasoning": "Text too short for analysis",
        }

    jurisdiction_list = create_jurisdiction_list()

    prompt = PRECISE_JURISDICTION_DETECTION_PROMPT.format(
        jurisdiction_list=jurisdiction_list,
        text=text[:5000],
    )
    logger.debug("Prompting agent with structured output for jurisdiction detection")

    try:
        system_prompt = "You are an expert in legal systems and court jurisdictions worldwide. Analyze the court decision and identify the precise jurisdiction, legal system type, and provide your confidence level and reasoning."

        # Create and run agent
        selected_model = model or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
        agent = Agent(
            name="JurisdictionDetector",
            instructions=system_prompt,
            output_type=JurisdictionOutput,
            model=selected_model,
        )

        result = asyncio.run(Runner.run(agent, prompt)).final_output

        jurisdiction_name = result.precise_jurisdiction
        legal_system_type = result.legal_system_type
        jurisdiction_code = result.jurisdiction_code
        confidence = result.confidence
        reasoning = result.reasoning

        logger.debug("Detected jurisdiction: %s (%s) with confidence %s", jurisdiction_name, legal_system_type, confidence)

        # Validate against known jurisdictions
        jurisdictions = load_jurisdictions()

        if jurisdiction_name and jurisdiction_name != "Unknown":
            # Try exact match first
            for jurisdiction in jurisdictions:
                if jurisdiction["name"].lower() == jurisdiction_name.lower():
                    return {
                        "jurisdiction_name": jurisdiction["name"],
                        "legal_system_type": legal_system_type,
                        "jurisdiction_code": jurisdiction["code"],
                        "confidence": confidence,
                        "reasoning": reasoning,
                    }

            # Try partial match
            for jurisdiction in jurisdictions:
                if (
                    jurisdiction_name.lower() in jurisdiction["name"].lower()
                    or jurisdiction["name"].lower() in jurisdiction_name.lower()
                ):
                    return {
                        "jurisdiction_name": jurisdiction["name"],
                        "legal_system_type": legal_system_type,
                        "jurisdiction_code": jurisdiction["code"],
                        "confidence": confidence * 0.9,  # Reduce confidence slightly for partial match
                        "reasoning": reasoning + " (partial match)",
                    }

            # If we have a reasonable jurisdiction name but it's not in our list
            if len(jurisdiction_name) > 2 and jurisdiction_name not in ["Unknown", "unknown", "N/A", "None"]:
                return {
                    "jurisdiction_name": jurisdiction_name,
                    "legal_system_type": legal_system_type,
                    "jurisdiction_code": jurisdiction_code if jurisdiction_code != "UNK" else "N/A",
                    "confidence": confidence * 0.8,  # Reduce confidence for unknown jurisdiction
                    "reasoning": reasoning + " (not in standard jurisdiction list)",
                }

        return {
            "jurisdiction_name": "Unknown",
            "legal_system_type": "Unknown",
            "jurisdiction_code": "UNK",
            "confidence": 0.0,
            "reasoning": "Could not identify jurisdiction from the text",
        }

    except Exception as e:
        logger.error("Error in jurisdiction detection: %s", e)
        return {
            "jurisdiction_name": "Unknown",
            "legal_system_type": "Unknown",
            "jurisdiction_code": "UNK",
            "confidence": 0.0,
            "reasoning": f"Error during detection: {str(e)}",
        }
