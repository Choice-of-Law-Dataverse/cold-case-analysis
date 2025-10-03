import streamlit as st

from components.auth import initialize_auth, render_model_selector
from components.css import load_css
from components.main_workflow import render_main_workflow
from components.sidebar import render_sidebar
from utils.state_manager import initialize_col_state

# Initialize authentication
initialize_auth()

# Set page config
st.set_page_config(
    page_title="CoLD Case Analyzer",
    page_icon="https://choiceoflaw.blob.core.windows.net/assets/favicon/favicon.ico",
    layout="wide"
)

# Top-centered logo
st.markdown(
    """
    <div class="cold-main-logo">
        <a href="https://cold.global" target="_blank" rel="noopener noreferrer" aria-label="Open CoLD Global website in a new tab">
            <img src="https://choiceoflaw.blob.core.windows.net/assets/cold_logo.svg" alt="CoLD Logo" />
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Render model selector
render_model_selector()

# Load CSS and render sidebar
load_css()
render_sidebar()

# Title and description
st.title("CoLD Case Analyzer")
st.info("The CoLD Case Analyzer can make mistakes. Please review each answer carefully.")
st.markdown("""
This tool helps you analyze court decisions and get structured summaries. 
You can provide feedback to improve the analysis until you're satisfied with the result.
""")

# Initialize state
initialize_col_state()

# Render main workflow
render_main_workflow()
