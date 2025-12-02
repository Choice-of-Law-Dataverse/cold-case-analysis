# components/auth.py
"""
Authentication and model selection functionality.
"""

import streamlit as st


def initialize_auth():
    """Initialize authentication session state."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = ""
