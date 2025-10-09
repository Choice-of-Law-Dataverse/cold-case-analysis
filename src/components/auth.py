# components/auth.py
"""
Authentication and model selection functionality.
"""

import streamlit as st

import config


def initialize_auth():
    """Initialize authentication session state."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = ""


def render_model_selector():
    """
    Render the LLM model selection interface.

    Returns:
        str: The selected model name
    """

    if st.session_state.get("logged_in"):
        model_options = ["gpt-5-nano", "gpt-4.1-nano", "o4-mini", "gpt-5-mini", "o3"]
    else:
        model_options = ["gpt-5-nano"]

    if st.session_state.get("logged_in"):
        chosen_model = st.selectbox("Select LLM Model:", model_options, index=0, key="llm_model_select")

        config.llm = config.get_llm(chosen_model)

        return chosen_model
    else:
        config.llm = config.get_llm("gpt-5-nano")
        return "gpt-5-nano"
