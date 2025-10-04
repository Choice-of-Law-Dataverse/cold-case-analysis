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
        color: #FFFFFF !important;  /* white text for contrast */
        border-radius: 0 !important;
        padding: 8px 16px !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stButton button:hover {
        background-color: #5a3fd9 !important;  /* slightly darker cold-purple */
        color: #FFFFFF !important;  /* maintain white text on hover */
    }

    /* Ensure button text/label elements are also white */
    .stButton button p,
    .stButton button div,
    .stButton button span {
        color: #FFFFFF !important;
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
        position: relative;
    }

    .cold-sidebar-footer {
        margin: 24px 0 0 0;
    }

    .cold-sidebar-footer img {
        max-width: 140px;
        height: auto;
        opacity: 0.9;
    }

    .cold-sidebar-footer .label {
        font-size: 12px !important;
        color: #334155 !important; /* slate-700-ish */
        margin-top: 6px;
        display: block;
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

    /* Main top logo */
    .cold-main-logo {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 8px 0 4px 0;
    }

    .cold-main-logo img {
        max-width: 120px;
        height: auto;
        margin: 0 0 40px 0;
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

    /* Progress Banner Container */
    .progress-banner {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #6F4DFA 0%, #5a3fd9 100%);
        color: white;
        padding: 16px 24px;
        box-shadow: 0 -4px 12px rgba(111, 77, 250, 0.3);
        z-index: 9999;
        animation: slideUp 0.3s ease-out;
    }

    @keyframes slideUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    /* Progress Banner Content */
    .progress-banner-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    /* Message Text */
    .progress-banner-message {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: white !important;
        text-align: center;
    }

    /* Progress Bar Container - Squiggly Line Design */
    .progress-banner-bar-container {
        width: 100%;
        height: 40px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* SVG Squiggly Path */
    .progress-banner-bar-container svg {
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
    }

    /* Progress Dot - follows SVG path using offset-path */
    .progress-dot {
        width: 16px;
        height: 16px;
        background-color: #4CAF50;
        border-radius: 50%;
        position: absolute;
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.8);
        z-index: 2;
        offset-path: path('M 0,20 Q 25,10 50,20 T 100,20 Q 125,30 150,20 T 200,20 Q 225,10 250,20 T 300,20 Q 325,30 350,20 T 400,20');
        offset-distance: 0%;
        transition: offset-distance 0.5s ease-out;
    }

    /* Indeterminate Spinner - Squiggly Animation following path */
    .progress-banner-spinner {
        width: 16px;
        height: 16px;
        background-color: #4CAF50;
        border-radius: 50%;
        position: absolute;
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.8);
        z-index: 2;
        offset-path: path('M 0,20 Q 25,10 50,20 T 100,20 Q 125,30 150,20 T 200,20 Q 225,10 250,20 T 300,20 Q 325,30 350,20 T 400,20');
        animation: squigglyMove 3s ease-in-out infinite;
    }

    @keyframes squigglyMove {
        0% {
            offset-distance: 0%;
        }
        100% {
            offset-distance: 100%;
        }
    }

    /* Adjust main content to account for banner */
    .main .block-container {
        padding-bottom: 100px !important;
    }
    </style>
    """, unsafe_allow_html=True)
