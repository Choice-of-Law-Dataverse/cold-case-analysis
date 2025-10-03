#!/usr/bin/env python3

"""
Test script to verify that India-specific prompts are correctly selected.
"""

import sys

sys.path.append("/home/simon/dev/cold-case-analysis/cold_case_analyzer_agent/streamlit")

from prompts.prompt_selector import get_prompt_module


def test_india_prompt_selection():
    """Test that India prompts are selected when specific_jurisdiction='India'"""

    print("Testing India prompt selection...")

    # Test with India as specific jurisdiction (should use India prompts)
    print("\n1. Testing with specific_jurisdiction='India'")
    india_module = get_prompt_module("common-law", "analysis", specific_jurisdiction="India")
    print(f"Module used: {india_module.__name__}")

    # Test without specific jurisdiction (should use common-law prompts)
    print("\n2. Testing without specific jurisdiction")
    common_law_module = get_prompt_module("common-law", "analysis")
    print(f"Module used: {common_law_module.__name__}")

    # Test with specific_jurisdiction='India' but civil-law (should still use India)
    print("\n3. Testing with civil-law jurisdiction but India specific")
    india_civil_module = get_prompt_module("civil-law", "analysis", specific_jurisdiction="India")
    print(f"Module used: {india_civil_module.__name__}")

    # Test with different specific jurisdiction
    print("\n4. Testing with specific_jurisdiction='Canada'")
    canada_module = get_prompt_module("common-law", "analysis", specific_jurisdiction="Canada")
    print(f"Module used: {canada_module.__name__}")

    # Verify India prompts are different from common-law
    print("\n5. Comparing prompt contents...")
    if hasattr(india_module, "FACTS_PROMPT") and hasattr(common_law_module, "FACTS_PROMPT"):
        india_facts = india_module.FACTS_PROMPT[:100]  # First 100 chars
        common_facts = common_law_module.FACTS_PROMPT[:100]  # First 100 chars
        print(f"India FACTS_PROMPT start: {india_facts}...")
        print(f"Common-law FACTS_PROMPT start: {common_facts}...")
        print(f"Are they different? {india_facts != common_facts}")

    print("\nTest completed!")

if __name__ == "__main__":
    test_india_prompt_selection()
