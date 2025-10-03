# utils/data_loaders.py
"""
Data loading utilities for the CoLD Case Analyzer.
"""
import csv
from pathlib import Path

from utils.sample_cd import SAMPLE_COURT_DECISION


def load_valid_themes():
    """
    Load valid themes from the themes CSV file.
    
    Returns:
        list: List of valid theme strings
    """
    themes_csv = Path(__file__).parent.parent / "data" / "themes.csv"
    valid_themes = []

    try:
        with open(themes_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                valid_themes.append(row["Theme"])
    except FileNotFoundError:
        # Return empty list if themes file not found
        valid_themes = []

    return valid_themes


def get_demo_case_text():
    """
    Get the demo case text.
    
    Returns:
        str: The sample court decision text
    """
    return SAMPLE_COURT_DECISION
