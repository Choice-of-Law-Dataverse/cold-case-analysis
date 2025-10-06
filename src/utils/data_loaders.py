# utils/data_loaders.py
"""
Data loading utilities for the CoLD Case Analyzer.
"""
from utils.sample_cd import SAMPLE_COURT_DECISION
from utils.themes_extractor import fetch_themes_list


def load_valid_themes():
    """
    Load valid themes from the cached themes data.

    Returns:
        list: List of valid theme strings
    """
    return fetch_themes_list()


def get_demo_case_text():
    """
    Get the demo case text.

    Returns:
        str: The sample court decision text
    """
    return SAMPLE_COURT_DECISION
