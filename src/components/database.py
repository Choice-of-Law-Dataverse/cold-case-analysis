# components/database.py
"""
Database persistence functionality for the CoLD Case Analyzer.
"""

import json
import os

import logfire
import psycopg2
import streamlit as st


def save_to_db(state):
    """
    Persist the analysis state as JSON into PostgreSQL.

    Args:
        state: The analysis state dictionary to persist
    """
    with logfire.span("save_to_db"):
        try:
            case_citation_list = state.get("case_citation", [])
            case_citation_str = case_citation_list[-1] if case_citation_list else None

            state["source"] = "case-analyzer.cold.global"

            with psycopg2.connect(
                host=os.getenv("POSTGRESQL_HOST"),
                port=int(os.getenv("POSTGRESQL_PORT", "5432")),
                dbname=os.getenv("POSTGRESQL_DATABASE"),
                user=os.getenv("POSTGRESQL_USERNAME"),
                password=os.getenv("POSTGRESQL_PASSWORD"),
            ) as conn_pg:
                with conn_pg.cursor() as cur:
                    cur.execute(
                        "INSERT INTO suggestions_case_analyzer(username, case_citation, user_email, data) VALUES (%s, %s, %s, %s)",
                        (
                            state.get("username"),
                            case_citation_str,
                            state.get("user_email"),
                            json.dumps(state),
                        ),
                    )
                conn_pg.commit()
            return True
        except Exception as e:
            st.error(f"Failed to save results: {e}")
            return False
