import logging
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

try:
    from config import NOCODB_API_TOKEN, NOCODB_BASE_URL
except ImportError:
    NOCODB_BASE_URL = os.getenv("NOCODB_BASE_URL")
    NOCODB_API_TOKEN = os.getenv("NOCODB_API_TOKEN")


@dataclass(frozen=True)
class FilterCondition:
    column: str
    value: Any


class NocoDBService:
    def __init__(self, base_url: str, api_token: str | None = None):
        if not base_url:
            raise ValueError("NocoDB base URL not configured")
        self.base_url = base_url.rstrip("/")
        self.headers = {}
        if api_token:
            # X nocodb API token header
            self.headers["xc-token"] = api_token

    def get_row(self, table: str, record_id: str) -> dict:
        """
        Fetch full record data and metadata for a specific row from NocoDB.
        """
        logger.debug("Fetching row %s from table %s in NocoDB", record_id, table)
        url = f"{self.base_url}/{table}/{record_id}"
        logger.debug("NocoDBService.get_row: GET %s", url)
        logger.debug("NocoDBService headers: %s", self.headers)
        resp = requests.get(url, headers=self.headers)
        logger.debug("Response from nocoDB: %d %s", resp.status_code, resp.text)
        resp.raise_for_status()
        payload = resp.json()
        logger.debug("NocoDBService.get_row response payload: %s", payload)
        return payload

    def list_rows(
        self,
        table: str,
        filters: Sequence[FilterCondition] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Fetch records for a given table via NocoDB API, applying optional filters and paging through all pages.
        """
        records: list[dict[str, Any]] = []
        offset = 0
        where_clauses = []
        if filters:
            for filter_condition in filters:
                col = filter_condition.column
                val = filter_condition.value
                if "Relevant for Case Analysis" in col and val in ["true", "false", True, False]:
                    op = "eq"
                elif isinstance(val, str) and val not in ["true", "false"]:
                    op = "ct"
                else:
                    op = "eq"
                where_clauses.append(f"({col},{op},{val})")
        where_param = "~and".join(where_clauses) if where_clauses else None
        while True:
            url = f"{self.base_url}/{table}"
            params: dict[str, Any] = {"limit": limit, "offset": offset}
            if where_param:
                params["where"] = where_param
            logger.debug("NocoDBService.list_rows: GET %s with params %s", url, params)
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            payload = resp.json()
            if isinstance(payload, dict):
                batch = payload.get("list") or payload.get("data") or []
                page_info = payload.get("pageInfo", {})
                is_last = page_info.get("isLastPage", False)
            elif isinstance(payload, list):
                batch = payload
                is_last = True
            else:
                break
            if not batch:
                break
            records.extend(batch)
            if is_last or len(batch) < limit:
                break
            offset += limit
        return records


def remove_fields_prefix(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.replace("fields.", "", regex=False)
    return df


def process_list_like_values(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        list_mask = df[col].apply(lambda value: isinstance(value, list))
        if bool(list_mask.any()):
            df[col] = df[col].apply(lambda value: ",".join(map(str, value)) if isinstance(value, list) else value)
    return df


def fetch_themes_dataframe() -> pd.DataFrame:
    csv_path = os.path.join(os.path.dirname(__file__), "../data/themes.csv")

    if not NOCODB_BASE_URL:
        try:
            return pd.read_csv(csv_path)
        except Exception as e:
            logger.error("Failed to read themes from CSV: %s", e)
            return pd.DataFrame({"Theme": [], "Definition": []})

    filters = [FilterCondition("Relevant for Case Analysis", 1)]

    nocodb_service = NocoDBService(
        base_url=NOCODB_BASE_URL,
        api_token=NOCODB_API_TOKEN,
    )

    def _records_to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
        if not records:
            return pd.DataFrame({"Theme": [], "Definition": []})
        df: pd.DataFrame = pd.DataFrame(records)
        df = process_list_like_values(df)
        if "Relevant for Case Analysis" in df.columns:
            mask = df["Relevant for Case Analysis"].isin([True, "true", "True", 1])
            df = df.loc[mask]
        if df.empty:
            return pd.DataFrame({"Theme": [], "Definition": []})
        available_cols = [col for col in ("Keywords", "Definition") if col in df.columns]
        if not available_cols:
            return pd.DataFrame({"Theme": [], "Definition": []})
        df = df.loc[:, available_cols]
        if "Keywords" in df.columns:
            df = df.rename(columns={"Keywords": "Theme"})
        return df.reset_index(drop=True)

    try:
        records = nocodb_service.list_rows("Glossary", filters=filters)
        processed = _records_to_dataframe(records)
        if not processed.empty:
            return processed
    except Exception as error:
        logger.error("Error fetching themes from NocoDB: %s", error)

    try:
        logger.debug("Trying without API filters...")
        fallback_records = nocodb_service.list_rows("Glossary", filters=None)
        processed = _records_to_dataframe(fallback_records)
        if not processed.empty:
            return processed
    except Exception as fallback_error:
        logger.error("Fallback also failed: %s", fallback_error)

    try:
        logger.info("Falling back to CSV file for themes...")
        return pd.read_csv(csv_path)
    except Exception as csv_error:
        logger.error("Failed to read themes from CSV: %s", csv_error)
        return pd.DataFrame({"Theme": [], "Definition": []})


def filter_themes_by_list(themes_list: list[str]) -> str:
    """
    Returns a markdown table (string) of Theme|Definition
    for those themes in themes_list, using the already‐loaded THEMES_TABLE_DF.
    """
    if not themes_list or THEMES_TABLE_DF.empty:
        return "No themes available."
    # fast in‐memory filter
    filtered_df = THEMES_TABLE_DF.loc[THEMES_TABLE_DF["Theme"].isin(themes_list)]
    return format_themes_table(filtered_df)


def fetch_themes_list() -> list[str]:
    """
    Get the list of theme names from the cached dataframe.

    Returns:
        list[str]: List of theme names
    """
    return THEMES_TABLE_DF["Theme"].dropna().tolist()


def get_valid_themes_set() -> set[str]:
    """
    Get a set of valid theme names for validation purposes.

    Returns:
        set[str]: Set of theme names
    """
    return set(THEMES_TABLE_DF["Theme"].dropna().tolist())


def format_themes_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "No themes available."
    table_str = "| Theme | Definition |\n"
    table_str += "|-------|------------|\n"
    for _, row in df.iterrows():
        theme = str(row["Theme"]).replace("|", "\\|")
        definition = str(row["Definition"]).replace("|", "\\|")
        table_str += f"| {theme} | {definition} |\n"
    return table_str


THEMES_TABLE_DF = fetch_themes_dataframe()
CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/themes.csv")
# THEMES_TABLE_DF  = pd.read_csv(CSV_PATH)
THEMES_TABLE_STR = format_themes_table(THEMES_TABLE_DF)

# Save to CSV (run once to recreate)
if __name__ == "__main__":
    THEMES_TABLE_DF.to_csv(CSV_PATH, index=False)
    print(f"Themes saved to {CSV_PATH}")
