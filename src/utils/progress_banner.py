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
        # Determinate progress with dot following path
        dot_distance = progress * 100
        banner_html = f"""
        <div class="progress-banner">
            <div class="progress-banner-content">
                <div class="progress-banner-message">{message}</div>
                <div class="progress-banner-bar-container">
                    <svg viewBox="0 0 100 40" preserveAspectRatio="none">
                        <!-- Background squiggly path (light) -->
                        <path d="M 0,20 Q 6.25,10 12.5,20 T 25,20 Q 31.25,30 37.5,20 T 50,20 Q 56.25,10 62.5,20 T 75,20 Q 81.25,30 87.5,20 T 100,20"
                              stroke="rgba(255, 255, 255, 0.3)"
                              stroke-width="3"
                              fill="none"
                              vector-effect="non-scaling-stroke"/>
                        <!-- Progress squiggly path (white) -->
                        <path d="M 0,20 Q 6.25,10 12.5,20 T 25,20 Q 31.25,30 37.5,20 T 50,20 Q 56.25,10 62.5,20 T 75,20 Q 81.25,30 87.5,20 T 100,20"
                              stroke="white"
                              stroke-width="3"
                              fill="none"
                              vector-effect="non-scaling-stroke"
                              stroke-dasharray="1000"
                              stroke-dashoffset="{1000 - (progress * 1000)}"
                              style="transition: stroke-dashoffset 0.5s ease-out;"/>
                    </svg>
                    <div class='progress-dot' style='offset-distance: {dot_distance}%;'></div>
                </div>
            </div>
        </div>
        """
    else:
        # Indeterminate progress with spinning dot
        banner_html = """
        <div class="progress-banner">
            <div class="progress-banner-content">
                <div class="progress-banner-message">""" + message + """</div>
                <div class="progress-banner-bar-container">
                    <svg viewBox="0 0 100 40" preserveAspectRatio="none">
                        <path d="M 0,20 Q 6.25,10 12.5,20 T 25,20 Q 31.25,30 37.5,20 T 50,20 Q 56.25,10 62.5,20 T 75,20 Q 81.25,30 87.5,20 T 100,20"
                              stroke="rgba(255, 255, 255, 0.3)"
                              stroke-width="3"
                              fill="none"
                              vector-effect="non-scaling-stroke"/>
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
