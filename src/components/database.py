# components/database.py
"""
Database persistence functionality for the CoLD Case Analyzer.
"""

import json
import os

import psycopg2
import streamlit as st


def save_to_db(state):
    """
    Persist the analysis state as JSON into PostgreSQL.

    Args:
        state: The analysis state dictionary to persist
    """
    try:
        # Load Postgres credentials from environment variables (more consistent with rest of app)
        with psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST"),
            port=int(os.getenv("POSTGRESQL_PORT", "5432")),
            dbname=os.getenv("POSTGRESQL_DATABASE"),
            user=os.getenv("POSTGRESQL_USERNAME"),
            password=os.getenv("POSTGRESQL_PASSWORD"),
        ) as conn_pg:
            with conn_pg.cursor() as cur:
                # Ensure table and columns
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS suggestions_case_analyzer (
                        id SERIAL PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                cur.execute("ALTER TABLE suggestions_case_analyzer ADD COLUMN IF NOT EXISTS username TEXT;")
                cur.execute("ALTER TABLE suggestions_case_analyzer ADD COLUMN IF NOT EXISTS model TEXT;")
                cur.execute("ALTER TABLE suggestions_case_analyzer ADD COLUMN IF NOT EXISTS case_citation TEXT;")
                cur.execute("ALTER TABLE suggestions_case_analyzer ADD COLUMN IF NOT EXISTS user_email TEXT;")
                cur.execute("ALTER TABLE suggestions_case_analyzer ADD COLUMN IF NOT EXISTS data JSONB;")
                # Insert record with user, model, and citation
                cur.execute(
                    "INSERT INTO suggestions_case_analyzer(username, model, case_citation, user_email, data) VALUES (%s, %s, %s, %s, %s)",
                    (
                        state.get("username"),
                        state.get("model"),
                        state.get("case_citation"),
                        state.get("user_email"),
                        json.dumps(state),
                    ),
                )
            conn_pg.commit()
    except Exception as e:
        st.error(f"Failed to save results: {e}")
