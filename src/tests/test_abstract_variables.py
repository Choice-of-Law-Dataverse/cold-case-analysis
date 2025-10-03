#!/usr/bin/env python3

"""
Test the abstract function with different jurisdiction types to ensure correct variables are passed.
"""

import sys

sys.path.append("/home/simon/dev/cold-case-analysis/cold_case_analyzer_agent/streamlit")

def test_abstract_variable_handling():
    """Test that abstract function handles different jurisdiction variables correctly"""

    from prompts.prompt_selector import get_prompt_module

    print("Testing abstract prompt variable requirements...")

    # Test cases for different jurisdictions - using app format
    jurisdictions_to_test = [
        ("Civil-law jurisdiction", None),
        ("Common-law jurisdiction", None),
        ("Common-law jurisdiction", "India")
    ]

    for jurisdiction, specific_jurisdiction in jurisdictions_to_test:
        print(f"\n--- Testing {jurisdiction} jurisdiction" + (f" (specific: {specific_jurisdiction})" if specific_jurisdiction else "") + " ---")

        try:
            # Get the abstract prompt for this jurisdiction
            module = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction)
            abstract_prompt = module.ABSTRACT_PROMPT

            print(f"Module: {module.__name__}")

            # Extract variables from the prompt template
            import re
            variables = re.findall(r"\{(\w+)\}", abstract_prompt)
            unique_vars = list(set(variables))  # Remove duplicates
            unique_vars.sort()  # Sort for consistent output

            print(f"Required variables: {unique_vars}")

            # Test with sample data
            sample_data = {
                "text": "Sample court decision text",
                "classification": "Sample classification",
                "facts": "Sample facts",
                "pil_provisions": "Sample PIL provisions",
                "col_issue": "Sample COL issue",
                "court_position": "Sample court position",
                "obiter_dicta": "Sample obiter dicta",
                "dissenting_opinions": "Sample dissenting opinions"
            }

            # Try to format the prompt
            try:
                # Only use variables that are actually in the template
                format_vars = {var: sample_data[var] for var in unique_vars if var in sample_data}
                formatted = abstract_prompt.format(**format_vars)
                print("✅ Prompt formatting successful")

                # Show first 200 chars of formatted prompt
                print(f"Preview: {formatted[:200]}...")

            except KeyError as e:
                print(f"❌ Missing variable: {e}")
            except Exception as e:
                print(f"❌ Formatting error: {e}")

        except Exception as e:
            print(f"❌ Error loading module: {e}")

if __name__ == "__main__":
    test_abstract_variable_handling()
