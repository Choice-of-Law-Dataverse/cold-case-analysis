# components/progress_banner.py
"""
Reusable progress banner component that sticks to the bottom of the page.
"""

import streamlit as st


def show_progress_banner(message: str, progress: float | None = None):
    """
    Display a sticky progress banner at the bottom of the page.

    Args:
        message: The status message to display
        progress: Optional progress value between 0.0 and 1.0. If None, shows an indeterminate spinner.
    """
    # Create a container for the banner
    banner_html = f"""
    <div class="progress-banner">
        <div class="progress-banner-content">
            <div class="progress-banner-message">{message}</div>
            <div class="progress-banner-bar-container">
                {"<div class='progress-banner-bar' style='width: " + str(int(progress * 100)) + "%;'></div>" if progress is not None else "<div class='progress-banner-spinner'></div>"}
            </div>
        </div>
    </div>
    """

    st.markdown(banner_html, unsafe_allow_html=True)


def add_progress_banner_css():
    """
    Add CSS styling for the progress banner.
    Should be called once at app initialization.
    """
    st.markdown(
        """
    <style>
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

    /* Progress Bar Container */
    .progress-banner-bar-container {
        width: 100%;
        height: 8px;
        background-color: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
        overflow: hidden;
        position: relative;
    }

    /* Progress Bar Fill */
    .progress-banner-bar {
        height: 100%;
        background-color: white;
        border-radius: 4px;
        transition: width 0.3s ease-out;
    }

    /* Indeterminate Spinner */
    .progress-banner-spinner {
        height: 100%;
        width: 30%;
        background-color: white;
        border-radius: 4px;
        animation: indeterminate 1.5s infinite;
    }

    @keyframes indeterminate {
        0% {
            transform: translateX(-100%);
        }
        100% {
            transform: translateX(400%);
        }
    }

    /* Adjust main content to account for banner */
    .main .block-container {
        padding-bottom: 100px !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
