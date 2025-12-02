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
            with psycopg2.connect(
                host=os.getenv("POSTGRESQL_HOST"),
                port=int(os.getenv("POSTGRESQL_PORT", "5432")),
                dbname=os.getenv("POSTGRESQL_DATABASE"),
                user=os.getenv("POSTGRESQL_USERNAME"),
                password=os.getenv("POSTGRESQL_PASSWORD"),
            ) as conn_pg:
                with conn_pg.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS suggestions_case_analyzer (
                            id SERIAL PRIMARY KEY,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        """
                    )
                    cur.execute("ALTER TABLE suggestions_case_analyzer ADD COLUMN IF NOT EXISTS username TEXT;")
                    cur.execute("ALTER TABLE suggestions_case_analyzer ADD COLUMN IF NOT EXISTS case_citation TEXT;")
                    cur.execute("ALTER TABLE suggestions_case_analyzer ADD COLUMN IF NOT EXISTS user_email TEXT;")
                    cur.execute("ALTER TABLE suggestions_case_analyzer ADD COLUMN IF NOT EXISTS data JSONB;")
                    cur.execute(
                        "INSERT INTO suggestions_case_analyzer(username, case_citation, user_email, data) VALUES (%s, %s, %s, %s)",
                        (
                            state.get("username"),
                            state.get("case_citation"),
                            state.get("user_email"),
                            json.dumps(state),
                        ),
                    )
                conn_pg.commit()
            return True
        except Exception as e:
            st.error(f"Failed to save results: {e}")
            return False
