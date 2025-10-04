"""
Test that logging has been properly implemented and print statements removed.
"""
import os
import re


def test_no_print_statements_in_tools():
    """Test that print statements have been replaced with logging in tools."""
    tools_dir = os.path.join(os.path.dirname(__file__), "..", "tools")
    
    files_to_check = [
        "case_analyzer.py",
        "col_extractor.py",
        "jurisdiction_detector.py",
        "precise_jurisdiction_detector.py",
        "themes_classifier.py"
    ]
    
    for filename in files_to_check:
        filepath = os.path.join(tools_dir, filename)
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        
        # Check for print statements (excluding comments)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            # Check for print statements
            if re.search(r'\bprint\s*\(', line):
                raise AssertionError(
                    f"Found print statement in {filename} at line {i}: {line.strip()}"
                )


def test_logging_imports():
    """Test that logging has been imported in modified files."""
    files_with_logging = {
        "case_analyzer.py": "tools",
        "col_extractor.py": "tools",
        "jurisdiction_detector.py": "tools",
        "precise_jurisdiction_detector.py": "tools",
        "themes_classifier.py": "tools",
        "themes_extractor.py": "utils",
        "debug_print_state.py": "utils",
        "pil_provisions_handler.py": "components"
    }
    
    for filename, subdir in files_with_logging.items():
        filepath = os.path.join(os.path.dirname(__file__), "..", subdir, filename)
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        
        # Check for logging import
        if "import logging" not in content:
            raise AssertionError(f"Missing 'import logging' in {filename}")
        
        # Check for logger creation
        if "logger = logging.getLogger(__name__)" not in content:
            raise AssertionError(f"Missing logger creation in {filename}")


def test_no_redundant_comments_in_case_analyzer():
    """Test that redundant comments have been removed from case_analyzer.py."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "tools", "case_analyzer.py")
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    
    redundant_patterns = [
        "# append relevant facts",
        "# append col_issue",
        "# append courts_position",
        "# return full updated lists",
        "# Get dynamic system prompt based on jurisdiction",
    ]
    
    for pattern in redundant_patterns:
        if pattern in content:
            raise AssertionError(
                f"Found redundant comment in case_analyzer.py: '{pattern}'"
            )


def test_style_guide_exists():
    """Test that the style guide documentation has been created."""
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs")
    style_guide_path = os.path.join(docs_dir, "STYLE_GUIDE.md")
    
    assert os.path.exists(style_guide_path), "STYLE_GUIDE.md not found in docs/"
    
    with open(style_guide_path, encoding="utf-8") as f:
        content = f.read()
    
    # Check for key sections
    required_sections = [
        "Logging Guidelines",
        "Comment Guidelines",
        "Use Logging, Not Print Statements",
        "Only Comment When Necessary"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section '{section}' in STYLE_GUIDE.md"


def test_readme_references_style_guide():
    """Test that README.md references the new style guide."""
    readme_path = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")
    
    with open(readme_path, encoding="utf-8") as f:
        content = f.read()
    
    assert "STYLE_GUIDE.md" in content, "README.md doesn't reference STYLE_GUIDE.md"
    assert "Coding Style Guide" in content, "README.md doesn't mention Coding Style Guide"


if __name__ == "__main__":
    import sys
    
    # Run all tests
    test_functions = [
        test_no_print_statements_in_tools,
        test_logging_imports,
        test_no_redundant_comments_in_case_analyzer,
        test_style_guide_exists,
        test_readme_references_style_guide
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
