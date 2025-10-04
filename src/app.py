import streamlit as st

from components.auth import initialize_auth, render_model_selector
from components.css import load_css
from components.main_workflow import render_main_workflow
from components.sidebar import render_sidebar
from utils.persistent_state import generate_session_id
from utils.state_manager import initialize_col_state, load_state_from_persistence, save_state_to_persistence

# Initialize authentication
initialize_auth()

# Handle session persistence
query_params = st.query_params
if "session_id" not in st.session_state:
    session_id = query_params.get("session_id")
    if session_id:
        load_state_from_persistence(session_id)
        st.session_state["session_id"] = session_id
    else:
        session_id = generate_session_id()
        st.session_state["session_id"] = session_id
        st.query_params["session_id"] = session_id
else:
    session_id = st.session_state["session_id"]
    if not query_params.get("session_id"):
        st.query_params["session_id"] = session_id

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

# Save state to persistence after rendering (at the end of each run)
save_state_to_persistence()
