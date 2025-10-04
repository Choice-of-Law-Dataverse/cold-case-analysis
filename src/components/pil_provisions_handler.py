# components/pil_provisions_handler.py
"""
PIL Provisions display and editing components.
"""
import logging
import re

import streamlit as st

logger = logging.getLogger(__name__)


def parse_pil_provisions(raw_content):
    """
    Parse PIL provisions content from various formats into structured data.

    Args:
        raw_content: Raw PIL provisions content (could be string or list)

    Returns:
        dict: Structured PIL data with categories
    """
    # Handle different input formats and ensure we have a string
    if isinstance(raw_content, list):
        if len(raw_content) == 1:
            content = str(raw_content[0])
        else:
            content = "\n".join(str(item) for item in raw_content)
    else:
        content = str(raw_content)

    # Remove outer list brackets if present
    content = content.strip()
    if content.startswith("['") and content.endswith("']"):
        content = content[2:-2]  # Remove [' and ']

    # Initialize structure
    parsed = {
        "judicial_precedents": [],
        "textbooks_sources": [],
        "statutory_provisions": [],
        "legal_principles": [],
        "summary": ""
    }

    # Parse different sections with more flexible patterns
    sections = {
        "judicial_precedents": r"\*\*Judicial Precedents:\*\*(.*?)(?=\n\*\*|$)",
        "textbooks_sources": r"\*\*Textbooks/Academic Sources:\*\*(.*?)(?=\n\*\*|$)",
        "statutory_provisions": r"\*\*Statutory Provisions:\*\*(.*?)(?=\n\*\*|$)",
        "legal_principles": r"\*\*Legal Principles:\*\*(.*?)(?=\n\*\*|$)",
        "summary": r"\*\*Summary[^:]*:\*\*(.*?)(?=\n\*\*|$)"
    }

    for key, pattern in sections.items():
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            section_content = match.group(1).strip()
            if key == "summary":
                parsed[key] = section_content
            else:
                # Split by lines and clean up
                lines = section_content.split("\n")
                items = []
                current_item = ""

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Check if it's a new item (starts with - or bullet)
                    if line.startswith("-") or line.startswith("•"):
                        if current_item:
                            items.append(current_item.strip())
                        current_item = line.lstrip("-•").strip()
                    else:
                        # Continuation of previous item
                        if current_item:
                            current_item += " " + line
                        else:
                            current_item = line

                # Add the last item
                if current_item:
                    items.append(current_item.strip())

                parsed[key] = [item for item in items if item and not item.startswith("*")]

    return parsed


def format_pil_for_display(parsed_data):
    """
    Format parsed PIL data for user-friendly display.

    Args:
        parsed_data: Structured PIL data

    Returns:
        str: Formatted content for display
    """
    sections = []

    if parsed_data["judicial_precedents"]:
        sections.append("**Judicial Precedents:**")
        for case in parsed_data["judicial_precedents"]:
            sections.append(f"• {case}")
        sections.append("")

    if parsed_data["textbooks_sources"]:
        sections.append("**Textbooks/Academic Sources:**")
        for source in parsed_data["textbooks_sources"]:
            sections.append(f"• {source}")
        sections.append("")

    if parsed_data["statutory_provisions"]:
        sections.append("**Statutory Provisions:**")
        for provision in parsed_data["statutory_provisions"]:
            sections.append(f"• {provision}")
        sections.append("")

    if parsed_data["legal_principles"]:
        sections.append("**Legal Principles:**")
        for principle in parsed_data["legal_principles"]:
            sections.append(f"• {principle}")
        sections.append("")

    if parsed_data["summary"]:
        sections.append("**Summary:**")
        sections.append(parsed_data["summary"])

    return "\n".join(sections)


def format_pil_for_storage(edited_content):
    """
    Convert edited content back to storage format.

    Args:
        edited_content: User-edited content string

    Returns:
        list: Content formatted for storage (maintains compatibility)
    """
    return [edited_content]


def display_pil_provisions(state, step_name="pil_provisions"):
    """
    Display PIL provisions in a user-friendly format.

    Args:
        state: Current analysis state
        step_name: Name of the PIL provisions step
    """
    raw_content = state.get(step_name, [])

    if not raw_content:
        return None

    logger.debug("raw_content type: %s", type(raw_content))
    logger.debug("raw_content: %s", raw_content)

    if isinstance(raw_content, list) and len(raw_content) >= 1:
        content_str = raw_content[-1]
        if isinstance(content_str, list):
            content_str = str(content_str)
    else:
        content_str = str(raw_content)

    content_str = str(content_str)

    logger.debug("content_str type: %s", type(content_str))
    logger.debug("content_str preview: %s...", content_str[:100])

    if content_str.strip().startswith("[") and content_str.strip().endswith("]"):
        try:
            import ast
            provision_list = ast.literal_eval(content_str)
            if isinstance(provision_list, list) and all(isinstance(item, str) for item in provision_list):
                formatted_content = "**Private International Law Sources:**\n\n"
                formatted_content += "\n".join([f"• {item}" for item in provision_list])
                return formatted_content
        except (ValueError, SyntaxError):
            pass
    try:
        parsed_data = parse_pil_provisions(content_str)

        # Check if we got any meaningful data
        has_content = any(parsed_data[key] for key in parsed_data if key != "summary") or parsed_data["summary"]

        if has_content:
            formatted_content = format_pil_for_display(parsed_data)
            return formatted_content
    except Exception:
        # If parsing fails, fall back to raw content
        pass

    # Fallback - clean up the raw content for display
    try:
        clean_content = content_str.replace("\\n", "\n").strip()
        if clean_content.startswith("['") and clean_content.endswith("']"):
            clean_content = clean_content[2:-2]
        return clean_content
    except Exception:
        # Final fallback - return string representation
        return str(content_str)


def handle_pil_provisions_editing(state, step_name, display_name, formatted_content):
    """
    Handle the editing interface for PIL provisions.

    Args:
        state: Current analysis state
        step_name: Name of the PIL provisions step
        display_name: Display name for the step
        formatted_content: Formatted content for editing

    Returns:
        bool: True if editing interface was shown
    """
    edit_key = f"{step_name}_edited"

    # Show editing interface
    st.markdown("**Edit Instructions:**")
    st.info("""
    You can edit the PIL provisions below. Use the following format:
    - Use • or - for bullet points
    - Keep section headers like **Judicial Precedents:** if needed
    - Separate different sections with empty lines
    """)

    edited = st.text_area(
        f"Edit {display_name}:",
        value=state.get(edit_key, formatted_content),
        height=300,
        key=f"{step_name}_edit_area",
        help="Edit the PIL provisions using the format shown above"
    )

    return edited


def update_pil_provisions_state(state, step_name, edited_content):
    """
    Update the state with edited PIL provisions content.

    Args:
        state: Current analysis state
        step_name: Name of the PIL provisions step
        edited_content: User-edited content
    """
    # Store in compatible format
    format_pil_for_storage(edited_content)
    state[step_name][-1] = edited_content  # Update last entry
    state[f"{step_name}_edited"] = edited_content  # Store edited version
