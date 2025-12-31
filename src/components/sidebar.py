import streamlit as st


def render_sidebar():
    """
    Render the sidebar with login controls, instructions, and documentation.
    """
    with st.sidebar:
        st.subheader("Login")

        try:
            if hasattr(st, "user") and st.user.is_logged_in:
                st.success(f"Logged in as: {st.user.email}")
                if st.button("Log out"):
                    st.logout()
            else:
                if st.button("Log in or Sign up"):
                    st.login("auth0")
        except Exception:
            st.info("Not logged in")

        st.header("How to Use")
        st.markdown("""
 1. Search for a case in the [Choice of Law Dataverse](https://cold.global).
 2. Upload the PDF file for text extraction or copy and paste the decision content.
 3. Click to detect the jurisdiction.
 4. Confirm the jurisdiction and its legal system. The tool adapts to different contexts (Civil Law or Common Law).
 5. The extraction process begins automatically (please note that after the first step, it may take a couple of minutes for the second step to be completed). You can monitor active processing through the running indicators at the top of the page.
 6. The system processes the decision through a structured workflow. A complete summary is generated within five minutes. Please note that outputs are structured in English regardless of the input language, except for Choice of Law Sections.
 7. Once the results are displayed, you can review the content and the system's confidence level as to the quality of the analysis.
 8. Each category is editable. You can modify the case citation if necessary and select different theme tags within our research scope. If no indicated theme applies to the decision, use the tag “NA”.
 9. The system tends to overextract “Choice of Law Section”. You can delete parts that are not relevant for the analysis.
 10. If you notice any mistakes in the generated text for Relevant Facts, Sources, Choice of Law Issue, Court’s Position, and Abstract, please remove them before submitting a final analysis.
 11. You can provide your contact information to become a registered Case Analyzer user and gain access to additional features using your login credentials.
 12. Click to submit your (revised) analysis. You can then print or save a copy of the results for your records.

This tool is powered by OpenAI's GPT-5. It serves as a guide to be used alongside the original court decision, which may be in a foreign language. We recommend verifying the information, as the Case Analyzer may occasionally produce errors.
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
                if st.session_state.get("precise_jurisdiction_confirmed") and st.session_state.get("precise_jurisdiction"):
                    jurisdiction_name = st.session_state.get("precise_jurisdiction")
                    legal_system_type = st.session_state.get("legal_system_type", "Unknown")

                    st.write(f"**Current Jurisdiction:** {jurisdiction_name}")
                    st.write(f"**Legal System:** {legal_system_type}")

                    if st.button("Preview System Prompt", key="preview_prompt"):
                        from utils.system_prompt_generator import generate_jurisdiction_specific_prompt

                        prompt = generate_jurisdiction_specific_prompt(jurisdiction_name, legal_system_type)
                        st.text_area("AI System Prompt:", value=prompt, height=200, disabled=True)

        # # documentation download
        # doc_path = Path(__file__).parent.parent / "user_documentation.pdf"
        # try:
        #     with open(doc_path, "rb") as doc_file:
        #         doc_bytes = doc_file.read()
        #     st.download_button(
        #         label="Download User Documentation", data=doc_bytes, file_name="user_documentation.pdf", mime="application/pdf"
        #     )
        # except Exception as e:
        #     st.error(f"Unable to load documentation: {e}")

        # # clear history button
        # if st.button("Clear History", key="clear_history"):
        #     st.session_state.clear()
        #     st.rerun()

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
