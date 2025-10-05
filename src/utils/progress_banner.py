"""
Centralized progress banner management to avoid multiple banners flickering.
"""
import streamlit as st


def get_banner_placeholder():
    """
    Get or create a persistent banner placeholder in session state.
    This ensures only one banner exists across all operations.
    """
    if "progress_banner_placeholder" not in st.session_state:
        # Create placeholder at the top level only once
        st.session_state.progress_banner_placeholder = st.empty()
    return st.session_state.progress_banner_placeholder


def show_progress_banner(message, progress=None):
    """
    Display a progress banner with squiggly line animation.

    Args:
        message: The message to display
        progress: Optional progress value (0.0 to 1.0) for determinate progress,
                 None for indeterminate progress
    """
    placeholder = get_banner_placeholder()

    if progress is not None:
        clip_percent = progress * 100
        banner_html = f"""
        <div class="progress-banner">
            <div class="progress-banner-content">
                <div class="progress-banner-message">{message}</div>
                <div class="progress-banner-bar-container">
                    <svg viewBox="0 0 120 50" preserveAspectRatio="none">
                        <defs>
                            <clipPath id="progressClip">
                                <rect x="0" y="0" width="{clip_percent}%" height="50"/>
                            </clipPath>
                        </defs>
                        <!-- Background path (light) with dots at ends -->
                        <path d="M 5,25 Q 12,10 20,25 Q 28,40 35,25 Q 42,15 50,30 Q 58,45 65,25 Q 72,10 80,25 Q 88,35 95,20 Q 102,10 110,25 L 115,25"
                              stroke="rgba(255, 255, 255, 0.3)"
                              stroke-width="3"
                              fill="none"
                              stroke-linecap="round"
                              vector-effect="non-scaling-stroke"/>
                        <circle cx="5" cy="25" r="4" fill="rgba(255, 255, 255, 0.3)"/>
                        <circle cx="115" cy="25" r="4" fill="rgba(255, 255, 255, 0.3)"/>
                        <!-- Progress path (white) with clipping and dots -->
                        <g clip-path="url(#progressClip)">
                            <path d="M 5,25 Q 12,10 20,25 Q 28,40 35,25 Q 42,15 50,30 Q 58,45 65,25 Q 72,10 80,25 Q 88,35 95,20 Q 102,10 110,25 L 115,25"
                                  stroke="white"
                                  stroke-width="3"
                                  fill="none"
                                  stroke-linecap="round"
                                  vector-effect="non-scaling-stroke"
                                  style="transition: opacity 0.5s ease-out;"/>
                            <circle cx="5" cy="25" r="4" fill="white"/>
                            <circle cx="115" cy="25" r="4" fill="white"/>
                        </g>
                    </svg>
                </div>
            </div>
        </div>
        """
    else:
        banner_html = """
        <div class="progress-banner">
            <div class="progress-banner-content">
                <div class="progress-banner-message">""" + message + """</div>
                <div class="progress-banner-bar-container">
                    <svg viewBox="0 0 120 50" preserveAspectRatio="none">
                        <!-- Background path (light) with dots at ends -->
                        <path d="M 5,25 Q 12,10 20,25 Q 28,40 35,25 Q 42,15 50,30 Q 58,45 65,25 Q 72,10 80,25 Q 88,35 95,20 Q 102,10 110,25 L 115,25"
                              stroke="rgba(255, 255, 255, 0.3)"
                              stroke-width="3"
                              fill="none"
                              stroke-linecap="round"
                              vector-effect="non-scaling-stroke"/>
                        <circle cx="5" cy="25" r="4" fill="rgba(255, 255, 255, 0.3)"/>
                        <circle cx="115" cy="25" r="4" fill="rgba(255, 255, 255, 0.3)"/>
                    </svg>
                    <div class='progress-banner-spinner'></div>
                </div>
            </div>
        </div>
        """

    with placeholder:
        st.markdown(banner_html, unsafe_allow_html=True)


def hide_progress_banner():
    """Clear the progress banner."""
    placeholder = get_banner_placeholder()
    placeholder.empty()
