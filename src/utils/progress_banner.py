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
                    <svg viewBox="0 0 120 60" preserveAspectRatio="none">
                        <defs>
                            <clipPath id="progressClip">
                                <rect x="0" y="0" width="{clip_percent}%" height="60"/>
                            </clipPath>
                        </defs>
                        <!-- Green dots at both ends -->
                        <circle cx="8" cy="30" r="6" fill="#4CAF50"/>
                        <circle cx="112" cy="30" r="6" fill="#4CAF50"/>
                        <!-- Background double line (semi-transparent white) -->
                        <path d="M 8,30 Q 20,15 35,25 Q 50,35 65,25 Q 80,15 95,25 Q 105,30 112,30"
                              stroke="rgba(255,255,255,0.3)"
                              stroke-width="2"
                              fill="none"
                              vector-effect="non-scaling-stroke"/>
                        <path d="M 8,30 Q 20,15 35,25 Q 50,35 65,25 Q 80,15 95,25 Q 105,30 112,30"
                              stroke="rgba(255,255,255,0.3)"
                              stroke-width="2"
                              fill="none"
                              vector-effect="non-scaling-stroke"
                              transform="translate(0, 3)"/>
                        <!-- Progress double line (white) with clipping -->
                        <g clip-path="url(#progressClip)">
                            <path d="M 8,30 Q 20,15 35,25 Q 50,35 65,25 Q 80,15 95,25 Q 105,30 112,30"
                                  stroke="white"
                                  stroke-width="2"
                                  fill="none"
                                  vector-effect="non-scaling-stroke"
                                  style="transition: opacity 0.5s ease-out;"/>
                            <path d="M 8,30 Q 20,15 35,25 Q 50,35 65,25 Q 80,15 95,25 Q 105,30 112,30"
                                  stroke="white"
                                  stroke-width="2"
                                  fill="none"
                                  vector-effect="non-scaling-stroke"
                                  transform="translate(0, 3)"
                                  style="transition: opacity 0.5s ease-out;"/>
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
                    <svg viewBox="0 0 120 60" preserveAspectRatio="none">
                        <defs>
                            <clipPath id="progressClipAnimated">
                                <rect x="0" y="0" width="100%" height="60" class="animated-clip"/>
                            </clipPath>
                        </defs>
                        <!-- Green dots at both ends -->
                        <circle cx="8" cy="30" r="6" fill="#4CAF50"/>
                        <circle cx="112" cy="30" r="6" fill="#4CAF50"/>
                        <!-- Background double line (semi-transparent white) -->
                        <path d="M 8,30 Q 20,15 35,25 Q 50,35 65,25 Q 80,15 95,25 Q 105,30 112,30"
                              stroke="rgba(255,255,255,0.3)"
                              stroke-width="2"
                              fill="none"
                              vector-effect="non-scaling-stroke"/>
                        <path d="M 8,30 Q 20,15 35,25 Q 50,35 65,25 Q 80,15 95,25 Q 105,30 112,30"
                              stroke="rgba(255,255,255,0.3)"
                              stroke-width="2"
                              fill="none"
                              vector-effect="non-scaling-stroke"
                              transform="translate(0, 3)"/>
                        <!-- Animated progress double line (white) -->
                        <g clip-path="url(#progressClipAnimated)">
                            <path d="M 8,30 Q 20,15 35,25 Q 50,35 65,25 Q 80,15 95,25 Q 105,30 112,30"
                                  stroke="white"
                                  stroke-width="2"
                                  fill="none"
                                  vector-effect="non-scaling-stroke"/>
                            <path d="M 8,30 Q 20,15 35,25 Q 50,35 65,25 Q 80,15 95,25 Q 105,30 112,30"
                                  stroke="white"
                                  stroke-width="2"
                                  fill="none"
                                  vector-effect="non-scaling-stroke"
                                  transform="translate(0, 3)"/>
                        </g>
                    </svg>
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
