import streamlit as st

from components.auth import initialize_auth, render_model_selector
from components.css import load_css
from components.main_workflow import render_main_workflow
from components.sidebar import render_sidebar
from utils.state_manager import initialize_col_state

initialize_auth()

st.set_page_config(
    page_title="CoLD Case Analyzer",
    page_icon="https://choiceoflaw.blob.core.windows.net/assets/favicon/favicon.ico",
    layout="wide",
)

st.markdown(
    """
    <div class="cold-main-logo">
        <a href="https://cold.global" target="_blank" rel="noopener noreferrer" aria-label="Open CoLD Global website in a new tab">
            <img src="https://choiceoflaw.blob.core.windows.net/assets/cold_logo.svg" alt="CoLD Logo" />
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
st.title("Case Analyzer")
st.markdown(
    """
<div class="app-description">

This is a free AI tool that helps you interpret private international law decisions. The accuracy of results may vary depending on case complexity.


Summaries are generated automatically within approximately five minutes after uploading the PDF and confirming the jurisdiction. The system extracts the main passages of the text (verbatim) pertinent to private international law, then organizes key information in English covering themes, relevant facts, applicable sources, choice of law issues, and the court's position on the choice of law issue. You can revise it and submit a final version of a case analysis.


This tool is part of the [Choice of Law Dataverse](https://cold.global) (CoLD) project. The results generated with the Case Analyzer are reviewed by researchers and can be integrated as descriptions of court decisions from multiple countries worldwide, contributing to comparative law research. The scope of analysis centers on party autonomy, i.e., cases addressing freedom of choice, non-State law, express and tacit choice, overriding mandatory rules, public policy, and absence of choice.


For details on the underlying methodology, please consult the prompting structure [documentation](https://github.com/Choice-of-Law-Dataverse/cold-case-analysis/blob/main/src/prompts/README.md).

</div>
""",
    unsafe_allow_html=True,
)

render_model_selector()
load_css()
render_sidebar()
initialize_col_state()
render_main_workflow()
