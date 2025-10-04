from pathlib import Path

import streamlit as st

import config


def render_sidebar():
    """
    Render the sidebar with login controls, instructions, and documentation.
    """
    credentials = config.USER_CREDENTIALS
    with st.sidebar:
        st.subheader("Login")
        if not st.session_state.get("logged_in"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", key="login_button"):
                if credentials.get(username) == password:
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = username
                    st.success(f"Logged in as {username}")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        else:
            st.write(f"Logged in as: {st.session_state['user']}")
            if st.button("Logout", key="logout_button"):
                st.session_state["logged_in"] = False
                st.session_state["user"] = ""
                st.success("Logged out")
                st.rerun()

        st.header("How to Use")
        st.markdown("""
        1. (Optional) Log in to access more advanced models
        2. Select the model you want to use
        3. Enter the case citation for the court decision
        4. Paste the full text of the court decision
        5. Click "Detect Jurisdiction" to classify the jurisdiction of the decision, evaluate its accuracy and optionally edit it
        6. Extract the Choice of Law section, evaluate it, and provide feedback
        7. Classify the court decision into themes, evaluate the classification, and edit if necessary
        8. Analyze the decision step-by-step, providing evaluations and edits as needed

        The analysis will include:
        - Abstract
        - Relevant Facts
        - Private International Law Provisions
        - Choice of Law Issue
        - Court's Position

        After evaluating and optionally editing the Court's Position, the analysis will be saved to a database. Note that results are only saved if you complete the analysis steps and click "Submit" at the end.
        You can clear the history at any time to start fresh.
        """)

        # Add dynamic system prompt testing section
        if st.session_state.get("logged_in"):
            with st.expander("🧪 Dynamic System Prompts", expanded=False):
                st.markdown("**New Feature: Jurisdiction-Specific AI Instructions**")
                st.markdown("""
                The system now automatically customizes AI instructions based on:
                - Detected jurisdiction (e.g., Germany, USA, India)
                - Legal system type (Civil law vs. Common law)
                - Jurisdiction-specific legal context

                This improves analysis accuracy by providing relevant legal framework information to the AI model.
                """)

                # Show current prompt if available
                if (st.session_state.get("precise_jurisdiction_confirmed") and
                    st.session_state.get("precise_jurisdiction")):

                    jurisdiction_name = st.session_state.get("precise_jurisdiction")
                    legal_system_type = st.session_state.get("legal_system_type", "Unknown")

                    st.write(f"**Current Jurisdiction:** {jurisdiction_name}")
                    st.write(f"**Legal System:** {legal_system_type}")

                    if st.button("Preview System Prompt", key="preview_prompt"):
                        from utils.system_prompt_generator import generate_jurisdiction_specific_prompt
                        prompt = generate_jurisdiction_specific_prompt(jurisdiction_name, legal_system_type)
                        st.text_area("AI System Prompt:", value=prompt, height=200, disabled=True)

        # documentation download
        doc_path = Path(__file__).parent.parent / "user_documentation.pdf"
        try:
            with open(doc_path, "rb") as doc_file:
                doc_bytes = doc_file.read()
            st.download_button(
                label="Download User Documentation",
                data=doc_bytes,
                file_name="user_documentation.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Unable to load documentation: {e}")

        # clear history button
        if st.button("Clear History", key="clear_history"):
            from utils.browser_storage import clear_all_storage
            clear_all_storage()
            st.session_state.clear()
            st.rerun()

        # restart analysis button (keeps user logged in)
        if st.button("Restart Analysis", key="restart_analysis"):
            from utils.state_manager import clear_analysis_state_only
            clear_analysis_state_only()
            st.rerun()

        # Footer endorsement and logo at the bottom of the sidebar
        st.markdown(
            """
            <div class="cold-sidebar-footer">
                <hr/>
                <img src="https://choiceoflaw.blob.core.windows.net/assets/universitaet-luzern-logo.svg" alt="University of Lucerne Logo" />
                <span class="label">Endorsed by the University of Lucerne</span>
                <br/>
                <img src="https://choiceoflaw.blob.core.windows.net/assets/snf-logo.svg" alt="Swiss National Science Foundation Logo" />
                <span class="label">Funded by the Swiss National Science Foundation</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
