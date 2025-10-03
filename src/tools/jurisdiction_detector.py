# tools/jurisdiction_detector.py
"""
Detects the jurisdiction type of a court decision: Civil-law, Common-law, or No court decision using an LLM.
"""
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

import config
from prompts.legal_system_type_detection import LEGAL_SYSTEM_TYPE_DETECTION_PROMPT


def get_jurisdiction_legal_system_mapping():
    """
    Load jurisdiction to legal system mapping from jurisdictions.csv.
    Returns a dictionary mapping jurisdiction names to legal system types.
    """
    mapping = {}

    # Known civil law jurisdictions based on jurisdictions.csv analysis
    civil_law_jurisdictions = {
        "Switzerland", "Germany", "France", "Italy", "Spain", "Austria", "Netherlands", "Belgium",
        "Luxembourg", "Portugal", "Greece", "Finland", "Sweden", "Denmark", "Norway", "Poland",
        "Czech Republic", "Slovakia", "Hungary", "Romania", "Bulgaria", "Croatia", "Slovenia",
        "Estonia", "Latvia", "Lithuania", "Malta", "Cyprus", "Japan", "South Korea", "China (Mainland)",
        "Taiwan", "Brazil", "Argentina", "Mexico", "Chile", "Colombia", "Peru", "Ecuador",
        "Bolivia", "Paraguay", "Uruguay", "Venezuela", "Russia", "Ukraine", "Turkey", "Egypt",
        "Morocco", "Tunisia", "Algeria", "Iran", "Lebanon", "Jordan", "Qatar", "Kuwait", "Bahrain",
        "UAE", "Saudi Arabia", "Israel", "Indonesia", "Thailand", "Vietnam", "Cambodia", "Laos",
        "Ethiopia", "Angola", "Mozambique", "Kazakhstan", "Uzbekistan", "Tajikistan", "Kyrgyzstan",
        "Belarus", "Moldova", "Georgia", "Armenia", "Azerbaijan", "Albania", "Bosnia and Herzegovina",
        "North Macedonia", "Montenegro", "Serbia", "Kosovo", "Iceland", "Liechtenstein", "Monaco",
        "San Marino", "Andorra", "European Union", "OHADA"
    }

    # Known common law jurisdictions
    common_law_jurisdictions = {
        "United States", "United States of America", "USA", "United Kingdom", "England", "Scotland",
        "Wales", "Northern Ireland", "Ireland", "Canada", "Australia", "New Zealand", "India",
        "Pakistan", "Bangladesh", "Sri Lanka", "Malaysia", "Singapore", "Hong Kong", "South Africa",
        "Nigeria", "Ghana", "Kenya", "Uganda", "Tanzania", "Zambia", "Zimbabwe", "Botswana",
        "Malawi", "Sierra Leone", "Gambia", "Jamaica", "Barbados", "Trinidad and Tobago",
        "Bahamas", "Belize", "Guyana", "Cyprus (Common Law aspects)", "Malta (Common Law aspects)",
        "Israel (Common Law aspects)", "Philippines", "Myanmar"
    }

    # Create the mapping
    for jurisdiction in civil_law_jurisdictions:
        mapping[jurisdiction.lower()] = "Civil-law jurisdiction"

    for jurisdiction in common_law_jurisdictions:
        mapping[jurisdiction.lower()] = "Common-law jurisdiction"

    return mapping

def _coerce_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(item) for item in content if item is not None)
    return str(content) if content is not None else ""


def detect_legal_system_by_jurisdiction(jurisdiction_name: str) -> str | None:
    """
    Detect legal system type based on jurisdiction name alone.
    Returns 'Civil-law jurisdiction', 'Common-law jurisdiction', or None if unknown.
    """
    if not jurisdiction_name or jurisdiction_name.lower() in ["unknown", "n/a", "none"]:
        return None

    mapping = get_jurisdiction_legal_system_mapping()

    # Direct lookup
    if jurisdiction_name.lower() in mapping:
        return mapping[jurisdiction_name.lower()]

    # Partial match lookup for compound names
    for mapped_jurisdiction, legal_system in mapping.items():
        if mapped_jurisdiction in jurisdiction_name.lower() or jurisdiction_name.lower() in mapped_jurisdiction:
            return legal_system

    return None

def detect_legal_system_type(jurisdiction_name: str, text: str) -> str:
    """
    Uses jurisdiction mapping first, then LLM analysis to classify the input text as:
    - 'Civil-law jurisdiction'
    - 'Common-law jurisdiction'
    - 'No court decision'
    """
    if not text or len(text.strip()) < 50:
        return "No court decision"

    # First, try to determine based on jurisdiction name
    jurisdiction_based_result = detect_legal_system_by_jurisdiction(jurisdiction_name)
    if jurisdiction_based_result:
        print(f"\nJurisdiction-based classification: {jurisdiction_name} -> {jurisdiction_based_result}")
        return jurisdiction_based_result

    # Fall back to LLM analysis with enhanced prompt
    prompt = LEGAL_SYSTEM_TYPE_DETECTION_PROMPT.format(jurisdiction_name=jurisdiction_name, text=text)
    print(f"\nUsing LLM analysis for jurisdiction: {jurisdiction_name}")
    print(f"Prompting LLM with:\n{prompt}\n")

    response = config.llm.invoke([
        SystemMessage(content="You are an expert in legal systems and court decisions."),
        HumanMessage(content=prompt)
    ])
    result = _coerce_to_text(getattr(response, "content", "")).strip()

    # Enforce output to be one of the three categories
    allowed = ["Civil-law jurisdiction", "Common-law jurisdiction", "No court decision"]
    for option in allowed:
        if option.lower() in result.lower():
            return option
    return "No court decision"
