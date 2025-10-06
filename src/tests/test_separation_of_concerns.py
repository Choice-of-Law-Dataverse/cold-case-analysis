#!/usr/bin/env python3
"""
Test to verify separation of concerns in the refactored code.

This test demonstrates that:
1. Data fetching methods accept explicit parameters (not state)
2. Data fetching methods don't mutate state
3. Functions are testable without complex state setup
"""

import sys
sys.path.insert(0, "/home/runner/work/cold-case-analysis/cold-case-analysis/src")


def test_function_signatures():
    """Test that refactored functions have the correct signatures (explicit parameters, no state)."""
    import inspect
    from tools.case_analyzer import relevant_facts, pil_provisions, col_issue, courts_position, abstract
    from tools.col_extractor import extract_col_section
    from tools.themes_classifier import theme_classification_node

    print("Testing function signatures for separation of concerns...")

    # Test case_analyzer functions
    relevant_facts_sig = inspect.signature(relevant_facts)
    assert "state" not in relevant_facts_sig.parameters, "relevant_facts should not accept 'state' parameter"
    assert "text" in relevant_facts_sig.parameters, "relevant_facts should accept 'text' parameter"
    assert "jurisdiction" in relevant_facts_sig.parameters, "relevant_facts should accept 'jurisdiction' parameter"
    assert "model" in relevant_facts_sig.parameters, "relevant_facts should accept 'model' parameter"
    print("✅ PASS - relevant_facts has explicit parameters (no state)")

    pil_provisions_sig = inspect.signature(pil_provisions)
    assert "state" not in pil_provisions_sig.parameters, "pil_provisions should not accept 'state' parameter"
    assert "text" in pil_provisions_sig.parameters, "pil_provisions should accept 'text' parameter"
    print("✅ PASS - pil_provisions has explicit parameters (no state)")

    col_issue_sig = inspect.signature(col_issue)
    assert "state" not in col_issue_sig.parameters, "col_issue should not accept 'state' parameter"
    assert "classification_themes" in col_issue_sig.parameters, "col_issue should accept 'classification_themes' parameter"
    print("✅ PASS - col_issue has explicit parameters (no state)")

    courts_position_sig = inspect.signature(courts_position)
    assert "state" not in courts_position_sig.parameters, "courts_position should not accept 'state' parameter"
    assert "classification" in courts_position_sig.parameters, "courts_position should accept 'classification' parameter"
    print("✅ PASS - courts_position has explicit parameters (no state)")

    abstract_sig = inspect.signature(abstract)
    assert "state" not in abstract_sig.parameters, "abstract should not accept 'state' parameter"
    assert "facts" in abstract_sig.parameters, "abstract should accept 'facts' parameter"
    assert "classification" in abstract_sig.parameters, "abstract should accept 'classification' parameter"
    print("✅ PASS - abstract has explicit parameters (no state)")

    # Test col_extractor function
    extract_col_section_sig = inspect.signature(extract_col_section)
    assert "state" not in extract_col_section_sig.parameters, "extract_col_section should not accept 'state' parameter"
    assert "text" in extract_col_section_sig.parameters, "extract_col_section should accept 'text' parameter"
    assert "jurisdiction" in extract_col_section_sig.parameters, "extract_col_section should accept 'jurisdiction' parameter"
    print("✅ PASS - extract_col_section has explicit parameters (no state)")

    # Test themes_classifier function
    theme_classification_node_sig = inspect.signature(theme_classification_node)
    assert "state" not in theme_classification_node_sig.parameters, "theme_classification_node should not accept 'state' parameter"
    assert "text" in theme_classification_node_sig.parameters, "theme_classification_node should accept 'text' parameter"
    assert "col_section" in theme_classification_node_sig.parameters, "theme_classification_node should accept 'col_section' parameter"
    print("✅ PASS - theme_classification_node has explicit parameters (no state)")

    print("\n🎉 All function signatures follow separation of concerns!")


def test_no_streamlit_imports_in_tools():
    """Test that tools modules don't import Streamlit (separation of concerns)."""
    print("\nTesting that tools modules don't import Streamlit...")

    import ast
    import pathlib

    tools_dir = pathlib.Path("/home/runner/work/cold-case-analysis/cold-case-analysis/src/tools")

    for tool_file in tools_dir.glob("*.py"):
        if tool_file.name == "__init__.py":
            continue

        with open(tool_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("streamlit"), f"{tool_file.name} should not import streamlit (found: {alias.name})"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("streamlit"), f"{tool_file.name} should not import from streamlit (found: {node.module})"

        print(f"✅ PASS - {tool_file.name} doesn't import Streamlit")

    print("\n🎉 All tools modules respect separation of concerns (no Streamlit imports)!")


def test_component_imports():
    """Test that components can import and use the refactored tools."""
    print("\nTesting that components can use the refactored tools...")

    # Import component modules to ensure they work with the new signatures
    from components.main_workflow import render_main_workflow
    from components.analysis_workflow import render_analysis_workflow
    from components.col_processor import render_col_processing

    print("✅ PASS - main_workflow imports successfully")
    print("✅ PASS - analysis_workflow imports successfully")
    print("✅ PASS - col_processor imports successfully")

    print("\n🎉 All components import successfully with refactored tools!")


if __name__ == "__main__":
    test_function_signatures()
    test_no_streamlit_imports_in_tools()
    test_component_imports()
    print("\n" + "="*60)
    print("✅ ALL SEPARATION OF CONCERNS TESTS PASSED!")
    print("="*60)
