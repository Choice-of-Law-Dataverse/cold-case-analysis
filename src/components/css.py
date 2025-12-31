import streamlit as st


def load_css():
    """
    Load custom CSS styling for chat and UI components.
    """
    st.markdown(
        """
    <style>

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

    /* Login required message */
    .login-required-message {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 20px;
        margin: 20px 0;
        border-radius: 4px;
    }

    .login-required-message p {
        margin: 0;
        color: #0F0035;
        font-size: 14px;
        line-height: 1.6;
    }

    .login-required-message strong {
        font-size: 16px;
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

    /* Print styles */
    @media print {
        /* Hide elements that shouldn't be printed */
        section[data-testid="stSidebar"],
        header[data-testid="stHeader"],
        .stButton,
        button,
        .cold-main-logo,
        footer,
        .stDeployButton,
        .machine-message,
        div[data-testid="stStatusWidget"],
        .stMarkdown:has(.cold-main-logo),
        .app-description,
        [role="tooltip"],
        .stTooltipHoverTarget,
        [data-testid="stTooltipHoverTarget"],
        [data-testid="stButton"] [title],
        button[title],
        .stButton button[title]:after,
        .stButton button[title]:before {
            display: none !important;
        }

        /* Ensure content fits on page */
        .stApp {
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Optimize text for printing */
        body, p, div, span {
            color: #000 !important;
            background: white !important;
            font-size: 12pt !important;
        }

        .stMarkdown p, .stMarkdown div, .stMarkdown span {
            font-size: 12pt !important;
        }

        /* Show links in full */
        a[href]:after {
            content: " (" attr(href) ")";
            font-size: 0.8em;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
