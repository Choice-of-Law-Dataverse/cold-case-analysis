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
                            <linearGradient id="pipeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" style="stop-color:rgba(255,255,255,0.5);stop-opacity:1" />
                                <stop offset="50%" style="stop-color:rgba(255,255,255,0.8);stop-opacity:1" />
                                <stop offset="100%" style="stop-color:rgba(255,255,255,0.5);stop-opacity:1" />
                            </linearGradient>
                            <linearGradient id="pipeGradientFilled" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" style="stop-color:rgba(255,255,255,0.7);stop-opacity:1" />
                                <stop offset="50%" style="stop-color:rgba(255,255,255,1);stop-opacity:1" />
                                <stop offset="100%" style="stop-color:rgba(255,255,255,0.7);stop-opacity:1" />
                            </linearGradient>
                        </defs>
                        <!-- Background pipe (light) with treasure map style path -->
                        <path d="M 8,30 Q 15,15 25,25 Q 30,30 35,35 Q 40,42 50,38 Q 55,36 58,30 Q 62,20 70,25 Q 75,28 78,35 Q 82,45 90,40 Q 95,37 98,30 Q 102,20 108,25 L 112,28"
                              stroke="url(#pipeGradient)"
                              stroke-width="8"
                              fill="none"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              vector-effect="non-scaling-stroke"
                              opacity="0.4"/>
                        <!-- Green circular dots at ends (background) -->
                        <circle cx="8" cy="30" r="4" fill="rgba(76, 175, 80, 0.4)"/>
                        <circle cx="112" cy="28" r="4" fill="rgba(76, 175, 80, 0.4)"/>
                        <!-- Progress pipe (white) with clipping -->
                        <g clip-path="url(#progressClip)">
                            <path d="M 8,30 Q 15,15 25,25 Q 30,30 35,35 Q 40,42 50,38 Q 55,36 58,30 Q 62,20 70,25 Q 75,28 78,35 Q 82,45 90,40 Q 95,37 98,30 Q 102,20 108,25 L 112,28"
                                  stroke="url(#pipeGradientFilled)"
                                  stroke-width="8"
                                  fill="none"
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                  vector-effect="non-scaling-stroke"
                                  style="transition: opacity 0.5s ease-out;"/>
                            <!-- Green circular dots at ends (filled) -->
                            <circle cx="8" cy="30" r="4" fill="#4CAF50"/>
                            <circle cx="112" cy="28" r="4" fill="#4CAF50"/>
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
                            <linearGradient id="pipeGradientStatic" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" style="stop-color:rgba(255,255,255,0.5);stop-opacity:1" />
                                <stop offset="50%" style="stop-color:rgba(255,255,255,0.8);stop-opacity:1" />
                                <stop offset="100%" style="stop-color:rgba(255,255,255,0.5);stop-opacity:1" />
                            </linearGradient>
                        </defs>
                        <!-- Background pipe with treasure map style path -->
                        <path d="M 8,30 Q 15,15 25,25 Q 30,30 35,35 Q 40,42 50,38 Q 55,36 58,30 Q 62,20 70,25 Q 75,28 78,35 Q 82,45 90,40 Q 95,37 98,30 Q 102,20 108,25 L 112,28"
                              stroke="url(#pipeGradientStatic)"
                              stroke-width="8"
                              fill="none"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              vector-effect="non-scaling-stroke"
                              opacity="0.4"/>
                        <!-- Green circular dots at ends -->
                        <circle cx="8" cy="30" r="4" fill="rgba(76, 175, 80, 0.4)"/>
                        <circle cx="112" cy="28" r="4" fill="rgba(76, 175, 80, 0.4)"/>
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
