#!/usr/bin/env python3
"""
Test script to verify the dynamic system prompt functionality.
Run this from the tests directory to test the implementation.
"""

import sys
from pathlib import Path

# Add the parent directory (streamlit) to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.system_prompt_generator import (
    generate_base_system_prompt,
    generate_jurisdiction_specific_prompt,
    get_system_prompt_for_analysis,
    load_jurisdiction_summaries,
)


def test_load_jurisdiction_summaries():
    """Test loading jurisdiction summaries from CSV."""
    print("Testing jurisdiction summaries loading...")
    summaries = load_jurisdiction_summaries()

    print(f"Loaded {len(summaries)} jurisdiction summaries")

    # Show first few examples
    for i, (jurisdiction, summary) in enumerate(summaries.items()):
        if i >= 3:  # Show only first 3 examples
            break
        print(f"\n{jurisdiction}:")
        print(f"  Summary: {summary[:100]}...")

    return len(summaries) > 0


def test_base_system_prompt():
    """Test basic system prompt generation."""
    print("\n" + "="*50)
    print("Testing base system prompt generation...")

    base_prompt = generate_base_system_prompt()
    print(f"Base prompt length: {len(base_prompt)} characters")
    print("Base prompt preview:")
    print(base_prompt[:200] + "...")

    return len(base_prompt) > 100


def test_jurisdiction_specific_prompt():
    """Test jurisdiction-specific prompt generation."""
    print("\n" + "="*50)
    print("Testing jurisdiction-specific prompt generation...")

    # Test with a known jurisdiction
    test_cases = [
        ("Germany", "Civil-law jurisdiction"),
        ("United States of America", "Common-law jurisdiction"),
        ("India", "Common-law jurisdiction"),
        ("Unknown", "Unknown legal system"),
        (None, None)
    ]

    for jurisdiction, legal_system in test_cases:
        print(f"\nTesting: {jurisdiction} ({legal_system})")
        prompt = generate_jurisdiction_specific_prompt(jurisdiction, legal_system)
        print(f"  Generated prompt length: {len(prompt)} characters")

        # Check if jurisdiction-specific context was added
        if jurisdiction and jurisdiction != "Unknown":
            if "JURISDICTION-SPECIFIC CONTEXT:" in prompt:
                print("  ✓ Jurisdiction-specific context added")
            else:
                print("  ⚠ No jurisdiction-specific context found")

        if legal_system and legal_system != "Unknown legal system":
            if "LEGAL SYSTEM CONTEXT:" in prompt:
                print("  ✓ Legal system context added")
            else:
                print("  ⚠ No legal system context found")


def test_state_based_prompt():
    """Test getting system prompt from analysis state."""
    print("\n" + "="*50)
    print("Testing state-based prompt generation...")

    # Simulate analysis states
    test_states = [
        {
            "precise_jurisdiction": "Germany",
            "jurisdiction": "Civil-law jurisdiction"
        },
        {
            "jurisdiction_name": "India",
            "legal_system_type": "Common-law jurisdiction"
        },
        {
            "precise_jurisdiction": "Unknown",
            "jurisdiction": "Unknown legal system"
        },
        {}  # Empty state
    ]

    for i, state in enumerate(test_states):
        print(f"\nTest state {i+1}: {state}")
        prompt = get_system_prompt_for_analysis(state)
        print(f"  Generated prompt length: {len(prompt)} characters")


def main():
    """Run all tests."""
    print("Dynamic System Prompt Implementation Test")
    print("=" * 60)

    tests = [
        test_load_jurisdiction_summaries,
        test_base_system_prompt,
        test_jurisdiction_specific_prompt,
        test_state_based_prompt
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result if result is not None else True)
        except Exception as e:
            print(f"ERROR in {test.__name__}: {e}")
            results.append(False)

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    test_names = [
        "Load Jurisdiction Summaries",
        "Generate Base System Prompt",
        "Generate Jurisdiction-Specific Prompt",
        "Generate State-Based Prompt"
    ]

    for i, (name, result) in enumerate(zip(test_names, results, strict=False)):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{i+1}. {name}: {status}")

    overall = "✓ ALL TESTS PASSED" if all(results) else "✗ SOME TESTS FAILED"
    print(f"\nOverall: {overall}")

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
