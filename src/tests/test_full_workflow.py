#!/usr/bin/env python3

"""
Integration test to verify the full jurisdiction detection and prompt selection workflow.
"""

import sys

sys.path.append("/home/simon/dev/cold-case-analysis/cold_case_analyzer_agent/streamlit")

from prompts.prompt_selector import get_prompt_module
from tools.precise_jurisdiction_detector import detect_precise_jurisdiction, determine_legal_system_type


def test_full_workflow():
    """Test the complete jurisdiction detection and prompt selection workflow"""

    # Sample Indian court decision text
    indian_text = """
    IN THE SUPREME COURT OF INDIA
    CIVIL APPELLATE JURISDICTION
    
    Case No: Civil Appeal No. 1234 of 2023
    
    Petitioner: ABC Ltd. v. Respondent: XYZ Corp.
    
    Before: Hon'ble Justice A.B. Singh and Hon'ble Justice C.D. Sharma
    
    JUDGMENT
    
    This case involves a dispute regarding a contract between an Indian company and a foreign entity. 
    The question of applicable law arises in this international commercial dispute involving choice of law principles.
    """

    print("Testing full workflow with Indian court decision...")

    try:
        # Step 1: Detect precise jurisdiction
        print("\nStep 1: Detecting precise jurisdiction...")
        jurisdiction_name = detect_precise_jurisdiction(indian_text)
        print(f"Detected jurisdiction: {jurisdiction_name}")

        # Step 2: Determine legal system type
        print(f"\nStep 2: Determining legal system type for '{jurisdiction_name}'...")
        legal_system = determine_legal_system_type(jurisdiction_name)
        print(f"Legal system: {legal_system}")

        # Step 3: Get appropriate prompts
        print(f"\nStep 3: Getting prompts for jurisdiction='{legal_system}', specific_jurisdiction='{jurisdiction_name}'...")

        # Test different prompt types
        analysis_module = get_prompt_module(legal_system, "analysis", jurisdiction_name)
        col_module = get_prompt_module(legal_system, "col_section", jurisdiction_name)
        theme_module = get_prompt_module(legal_system, "theme", jurisdiction_name)

        print(f"Analysis module: {analysis_module.__name__}")
        print(f"COL section module: {col_module.__name__}")
        print(f"Theme module: {theme_module.__name__}")

        # Step 4: Verify India-specific prompts are used if India is detected
        if jurisdiction_name and jurisdiction_name.lower() == "india":
            expected_module = "prompts.india."
            assert expected_module in analysis_module.__name__, f"Expected India prompts, got {analysis_module.__name__}"
            assert expected_module in col_module.__name__, f"Expected India prompts, got {col_module.__name__}"
            assert expected_module in theme_module.__name__, f"Expected India prompts, got {theme_module.__name__}"
            print("✅ India-specific prompts correctly selected!")
        else:
            print(f"ℹ️  Non-India jurisdiction detected: {jurisdiction_name}")

        # Step 5: Test that prompts can be accessed
        print("\nStep 5: Testing prompt accessibility...")
        if hasattr(analysis_module, "FACTS_PROMPT"):
            print("✅ FACTS_PROMPT accessible")
        if hasattr(col_module, "COL_SECTION_PROMPT"):
            print("✅ COL_SECTION_PROMPT accessible")
        if hasattr(theme_module, "PIL_THEME_PROMPT"):
            print("✅ PIL_THEME_PROMPT accessible")

        print("\n🎉 Full workflow test completed successfully!")

    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_workflow()
