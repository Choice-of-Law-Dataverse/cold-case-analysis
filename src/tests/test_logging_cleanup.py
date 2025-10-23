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
        "jurisdiction_classifier.py",
        "theme_classifier.py"
    ]

    for filename in files_to_check:
        filepath = os.path.join(tools_dir, filename)
        if not os.path.exists(filepath):
            continue
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check for print statements (excluding comments)
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#"):
                continue
            # Check for print statements
            if re.search(r"\bprint\s*\(", line):
                raise AssertionError(
                    f"Found print statement in {filename} at line {i}: {line.strip()}"
                )


def test_logging_imports():
    """Test that logging has been imported in modified files."""
    files_with_logging = {
        "case_analyzer.py": "tools",
        "col_extractor.py": "tools",
        "jurisdiction_classifier.py": "tools",
        "theme_classifier.py": "tools",
        "themes_extractor.py": "utils",
        "debug_print_state.py": "utils",
        "pil_provisions_handler.py": "components"
    }

    for filename, subdir in files_with_logging.items():
        filepath = os.path.join(os.path.dirname(__file__), "..", subdir, filename)
        if not os.path.exists(filepath):
            continue
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check for logging import
        if "import logging" not in content:
            raise AssertionError(f"Missing 'import logging' in {filename}")

        # Check for logger creation (may be using different patterns)
        if "logger = logging.getLogger" not in content and "logging." not in content:
            raise AssertionError(f"Missing logger usage in {filename}")


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


def test_conventions_in_agents_md():
    """Test that AGENTS.md contains coding conventions."""
    agents_path = os.path.join(os.path.dirname(__file__), "..", "..", "AGENTS.md")

    assert os.path.exists(agents_path), "AGENTS.md not found"

    with open(agents_path, encoding="utf-8") as f:
        content = f.read()

    required_sections = [
        "Coding Conventions",
        "Logging",
        "Comments",
    ]

    for section in required_sections:
        assert section in content, f"Missing section '{section}' in AGENTS.md"


def test_readme_references_agents_md():
    """Test that README.md references AGENTS.md for coding conventions."""
    readme_path = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")

    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    assert "AGENTS.md" in content, "README.md doesn't reference AGENTS.md"


if __name__ == "__main__":
    import sys

    test_functions = [
        test_no_print_statements_in_tools,
        test_logging_imports,
        test_no_redundant_comments_in_case_analyzer,
        test_conventions_in_agents_md,
        test_readme_references_agents_md
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
