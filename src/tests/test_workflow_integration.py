#!/usr/bin/env python3

"""
Test the complete workflow with abstract as final step using correct variables.
"""

import sys

sys.path.append("/home/simon/dev/cold-case-analysis/cold_case_analyzer_agent/streamlit")

def test_workflow_integration():
    """Test that the workflow handles abstract correctly for all jurisdictions"""

    print("Testing workflow integration with abstract as final step...")

    # Mock state data that would be available when abstract runs
    mock_states = {
        "Civil-law jurisdiction": {
            "full_text": "Sample court decision text",
            "jurisdiction": "Civil-law jurisdiction",
            "precise_jurisdiction": None,
            "classification": ["Contract law, Choice of law clause"],
            "relevant_facts": ["Facts about the international contract dispute"],
            "pil_provisions": ["Article 3 Rome I Regulation"],
            "col_issue": ["Can parties choose law with no connection?"],
            "courts_position": ["Parties have broad autonomy in choosing applicable law"]
        },
        "Common-law jurisdiction": {
            "full_text": "Sample court decision text",
            "jurisdiction": "Common-law jurisdiction",
            "precise_jurisdiction": None,
            "classification": ["Contract law, Choice of law clause"],
            "relevant_facts": ["Facts about the international contract dispute"],
            "pil_provisions": ["Vita Food case, proper law doctrine"],
            "col_issue": ["Can parties choose law with no connection?"],
            "courts_position": ["Parties have broad autonomy subject to bona fide connection"],
            "obiter_dicta": ["Court noted alternative approaches exist"],
            "dissenting_opinions": ["No dissenting opinion on choice of law"]
        },
        "India": {
            "full_text": "Sample court decision text",
            "jurisdiction": "Common-law jurisdiction",
            "precise_jurisdiction": "India",
            "classification": ["Contract law, Choice of law clause"],
            "relevant_facts": ["Facts about the international contract dispute"],
            "pil_provisions": ["Indian Contract Act, Choice of law principles"],
            "col_issue": ["Can parties choose foreign law in Indian courts?"],
            "courts_position": ["Indian courts will apply chosen foreign law if valid"],
            "obiter_dicta": ["Court noted importance of public policy considerations"],
            "dissenting_opinions": ["No dissenting opinion on choice of law"]
        }
    }

    for jurisdiction_name, state in mock_states.items():
        print(f"\n--- Testing {jurisdiction_name} workflow ---")

        try:
            # Simulate the abstract function logic
            from prompts.prompt_selector import get_prompt_module

            jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
            specific_jurisdiction = state.get("precise_jurisdiction")
            ABSTRACT_PROMPT = get_prompt_module(jurisdiction, "analysis", specific_jurisdiction).ABSTRACT_PROMPT

            # Get required variables for all jurisdictions
            classification = state.get("classification", [""])[-1] if state.get("classification") else ""
            facts = state.get("relevant_facts", [""])[-1] if state.get("relevant_facts") else ""
            pil_provisions = state.get("pil_provisions", [""])[-1] if state.get("pil_provisions") else ""
            col_issue = state.get("col_issue", [""])[-1] if state.get("col_issue") else ""
            court_position = state.get("courts_position", [""])[-1] if state.get("courts_position") else ""

            # Prepare base prompt variables
            prompt_vars = {
                "text": state["full_text"],
                "classification": classification,
                "facts": facts,
                "pil_provisions": pil_provisions,
                "col_issue": col_issue,
                "court_position": court_position
            }

            # Add common law / India specific variables if available
            if jurisdiction == "Common-law jurisdiction" or (specific_jurisdiction and specific_jurisdiction.lower() == "india"):
                obiter_dicta = state.get("obiter_dicta", [""])[-1] if state.get("obiter_dicta") else ""
                dissenting_opinions = state.get("dissenting_opinions", [""])[-1] if state.get("dissenting_opinions") else ""
                prompt_vars.update({
                    "obiter_dicta": obiter_dicta,
                    "dissenting_opinions": dissenting_opinions
                })

            # Test formatting the prompt
            formatted_prompt = ABSTRACT_PROMPT.format(**prompt_vars)

            print("✅ Abstract prompt formatted successfully")
            print(f"Variables used: {list(prompt_vars.keys())}")
            print(f"Module: {get_prompt_module(jurisdiction, 'analysis', specific_jurisdiction).__name__}")
            print(f"Preview: {formatted_prompt[:150]}...")

        except Exception as e:
            print(f"❌ Error in {jurisdiction_name} workflow: {e}")
            import traceback
            traceback.print_exc()

    print("\n🎉 Workflow integration test completed!")

if __name__ == "__main__":
    test_workflow_integration()
