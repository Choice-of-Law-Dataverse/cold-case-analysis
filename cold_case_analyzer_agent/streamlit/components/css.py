import streamlit as st


def load_css():
    """
    Load custom CSS styling for chat and UI components.
    """
    st.markdown("""
    <style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Base styles */
    body {
        font-family: 'Inter', sans-serif;
        color: #0F0035 !important;
    }

    /* Typography */
    h1 {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #0F0035 !important;
    }

    h2 {
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #0F0035 !important;
    }

    h3 {
        font-size: 20px !important;
        font-weight: 400 !important;
        color: #0F0035 !important;
    }

    p {
        font-size: 14px !important;
        line-height: 28px !important;
        color: #0F0035 !important;
    }

    /* Message containers */
    .message-container {
        display: flex;
        flex-direction: column;
        margin: 12px 0;
    }

    .message-header {
        font-size: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        margin-bottom: 6px;
        color: #0F0035;
    }

    /* User messages */
    .user-message {
        background-color: #f3f2fa;  /* cold-purple-fake-alpha */
        color: #0F0035;  /* cold-night */
        padding: 15px;
        border-radius: 0;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        margin-right: 0;
        border: 1px solid #6F4DFA;  /* cold-purple */
        font-size: 14px !important;
        line-height: 28px !important;
    }

    /* Machine messages */
    .machine-message {
        background-color: #FAFAFA;  /* cold-bg */
        color: #0F0035;  /* cold-night */
        padding: 15px;
        border-radius: 0;
        margin: 8px 0;
        max-width: 80%;
        margin-left: 0;
        margin-right: auto;
        border: 1px solid #E2E8F0;  /* cold-gray */
        font-size: 14px !important;
        line-height: 28px !important;
    }

    /* Input areas */
    .stTextArea textarea {
        font-family: 'Inter', sans-serif;
        font-size: 14px !important;
        line-height: 28px !important;
        color: #0F0035 !important;
        caret-color: #0F0035 !important;
        border: 1px solid #E2E8F0 !important;  /* cold-gray */
        border-radius: 0 !important;
        padding: 12px !important;
        background-color: #FAFAFA; !important;
    }

    .stTextArea textarea:focus {
        border-color: #6F4DFA !important;  /* cold-purple */
        box-shadow: none !important;
    }

    /* Buttons */
    .stButton button {
        font-family: 'Inter', sans-serif;
        font-size: 14px !important;
        font-weight: 400 !important;
        background-color: #6F4DFA !important;  /* cold-purple */
        color: white !important;
        border-radius: 0 !important;
        padding: 8px 16px !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stButton button:hover {
        background-color: #5a3fd9 !important;  /* slightly darker cold-purple */
    }

    /* Sliders */
    .stSlider {
        /* constrain slider width */
        max-width: 400px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FAFAFA !important;
        color: #0F0035 !important;
        border-right: 1px solid #E2E8F0 !important; /* optional, clean border */
    }

    /* Header */
    header[data-testid="stHeader"] {
        background-color: white !important;
        /*border-bottom: 1px solid #E2E8F0 !important;   cold-gray */
    }

    /* Warnings */
    .stWarning {
        background-color: #FFF0D9 !important;  /* cold-cream */
        border: 1px solid #FF9D00 !important;  /* label-legal-instrument */
        color: #0F0035 !important;  /* cold-night */
    }

    /* Main container */
    .stApp {
        background-color: white !important;
    }

    /* Lists */
    ul {
        list-style-type: disc;
        margin: 0 !important;
        padding: 0.5rem 0 1.5rem 1.5rem !important;
    }

    li {
        margin: 0 !important;
        color: #0F0035 !important;  /* cold-night */
    }

    li::marker {
        color: #0F0035 !important;  /* cold-night */
    }

    /* Links */
    a {
        color: #6F4DFA !important;  /* cold-purple */
        text-decoration: none !important;
        font-weight: 400 !important;
    }
    </style>
    """, unsafe_allow_html=True)
