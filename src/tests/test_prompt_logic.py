#!/usr/bin/env python3

"""
Simple test to verify prompt selection logic without LLM dependencies.
"""

import sys

sys.path.append("/home/simon/dev/cold-case-analysis/cold_case_analyzer_agent/streamlit")

def test_prompt_selection_logic():
    """Test prompt selection logic without requiring LLM"""

    # Import only the prompt selector
    from prompts.prompt_selector import get_prompt_module

    print("Testing prompt selection logic...")

    # Test cases
    test_cases = [
        # (jurisdiction, prompt_type, specific_jurisdiction, expected_module_pattern)
        ("common-law", "analysis", "India", "india"),
        ("civil-law", "analysis", "India", "india"),
        ("common-law", "col_section", "India", "india"),
        ("civil-law", "theme", "India", "india"),
        ("common-law", "analysis", None, "civil_law"),  # Default is civil_law
        ("civil-law", "analysis", None, "civil_law"),
        ("common-law", "analysis", "Canada", "civil_law"),  # Non-India falls back
        ("civil-law", "col_section", "Germany", "civil_law"),
    ]

    all_passed = True

    for jurisdiction, prompt_type, specific_jurisdiction, expected_pattern in test_cases:
        try:
            module = get_prompt_module(jurisdiction, prompt_type, specific_jurisdiction)
            module_name = module.__name__

            if expected_pattern in module_name:
                result = "✅ PASS"
            else:
                result = "❌ FAIL"
                all_passed = False

            print(f"{result} - get_prompt_module('{jurisdiction}', '{prompt_type}', '{specific_jurisdiction}') -> {module_name}")

        except Exception as e:
            print(f"❌ ERROR - get_prompt_module('{jurisdiction}', '{prompt_type}', '{specific_jurisdiction}') -> {e}")
            all_passed = False

    print(f"\n{'🎉 All tests passed!' if all_passed else '❌ Some tests failed!'}")

    # Test a specific case: India jurisdiction should use India prompts
    print("\n--- Detailed India Test ---")
    try:
        india_analysis = get_prompt_module("common-law", "analysis", "India")
        print(f"India analysis module: {india_analysis.__name__}")

        # Check if required prompts exist
        required_prompts = ["FACTS_PROMPT", "PIL_PROVISIONS_PROMPT", "COL_ISSUE_PROMPT", "COURTS_POSITION_PROMPT", "ABSTRACT_PROMPT"]
        for prompt_name in required_prompts:
            if hasattr(india_analysis, prompt_name):
                print(f"✅ {prompt_name} exists")
            else:
                print(f"❌ {prompt_name} missing")

    except Exception as e:
        print(f"❌ Error testing India prompts: {e}")

if __name__ == "__main__":
    test_prompt_selection_logic()
