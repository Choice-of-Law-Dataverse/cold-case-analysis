import logging
import os
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

# Add these to your config.py file:
# NOCODB_BASE_URL = os.getenv("NOCODB_BASE_URL")
# NOCODB_API_TOKEN = os.getenv("NOCODB_API_TOKEN")
try:
    from config import NOCODB_API_TOKEN, NOCODB_BASE_URL
except ImportError:
    # Fallback if not yet added to config
    NOCODB_BASE_URL = os.getenv("NOCODB_BASE_URL")
    NOCODB_API_TOKEN = os.getenv("NOCODB_API_TOKEN")

class NocoDBService:
    def __init__(self, base_url: str, api_token: str = None):
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
        print(f"Fetching row {record_id} from table {table} in NocoDB")
        logger = logging.getLogger(__name__)
        url = f"{self.base_url}/{table}/{record_id}"
        logger.debug("NocoDBService.get_row: GET %s", url)
        logger.debug("NocoDBService headers: %s", self.headers)
        resp = requests.get(url, headers=self.headers)
        print("Response from nocoDB:", resp.status_code, resp.text)
        resp.raise_for_status()
        payload = resp.json()
        logger.debug("NocoDBService.get_row response payload: %s", payload)
        # return full payload directly
        return payload

    def list_rows(self, table: str, filters: list = None, limit: int = 100) -> list:
        """
        Fetch records for a given table via NocoDB API, applying optional filters and paging through all pages.
        """
        logger = logging.getLogger(__name__)
        records = []
        offset = 0
        # build where parameter if filters provided
        where_clauses = []
        if filters:
            for f in filters:
                col = f.column
                val = f.value
                # choose operator based on column name and value type
                if "Relevant for Case Analysis" in col and val in ["true", "false", True, False]:
                    op = "eq"  # Use equals for boolean fields
                elif isinstance(val, str) and val not in ["true", "false"]:
                    op = "ct"  # Use contains for text strings
                else:
                    op = "eq"  # Use equals for everything else
                # escape comma or parentheses in val?
                where_clauses.append(f"({col},{op},{val})")
        where_param = "~and".join(where_clauses) if where_clauses else None
        while True:
            url = f"{self.base_url}/{table}"
            params = {"limit": limit, "offset": offset}
            if where_param:
                params["where"] = where_param
            logger.debug("NocoDBService.list_rows: GET %s with params %s", url, params)
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            payload = resp.json()
            # extract batch results
            if isinstance(payload, dict):
                batch = payload.get("list") or payload.get("data") or []
                # check pageInfo for last page
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

def remove_fields_prefix(df):
    df.columns = df.columns.str.replace("fields.", "")
    return df

def process_list_like_values(df):
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(
                lambda x: ",".join(map(str, x)) if isinstance(x, list) else x
            )
    return df

def fetch_themes_dataframe():
    # Create filter for "Relevant for Case Analysis" = True
    class Filter:
        def __init__(self, column, value):
            self.column = column
            self.value = value

    # Try different boolean representations that NocoDB might accept
    filters = [Filter("Relevant for Case Analysis", 1)]  # Try numeric boolean

    # You'll need to add these NocoDB config variables to your config.py
    # For now, using placeholder names - adjust as needed
    nocodb_service = NocoDBService(
        base_url=NOCODB_BASE_URL,  # Add this to config.py
        api_token=NOCODB_API_TOKEN  # Add this to config.py
    )

    try:
        records = nocodb_service.list_rows("Glossary", filters=filters)

        if not records:
            return pd.DataFrame(columns=["Theme", "Definition"])

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Process the data similar to Airtable version
        df = process_list_like_values(df)

        # Filter and select the required columns (double-check in case API filter didn't work)
        if "Relevant for Case Analysis" in df.columns:
            # Try multiple boolean representations
            df = df[
                (df["Relevant for Case Analysis"] == True) |
                (df["Relevant for Case Analysis"] == "true") |
                (df["Relevant for Case Analysis"] == "True") |
                (df["Relevant for Case Analysis"] == 1)
            ]

        # Select Keywords and Definition columns
        required_cols = ["Keywords", "Definition"]
        available_cols = [col for col in required_cols if col in df.columns]

        if not available_cols:
            return pd.DataFrame(columns=["Theme", "Definition"])

        df = df[available_cols]

        # Rename Keywords to Theme
        if "Keywords" in df.columns:
            df = df.rename(columns={"Keywords": "Theme"})

        df = df.reset_index(drop=True)
        return df

    except Exception as e:
        print(f"Error fetching themes from NocoDB: {e}")

        # Fallback: try without filters and filter in pandas
        try:
            print("Trying without API filters...")
            records = nocodb_service.list_rows("Glossary", filters=None)

            if not records:
                return pd.DataFrame(columns=["Theme", "Definition"])

            df = pd.DataFrame(records)
            df = process_list_like_values(df)

            # Filter in pandas instead of API
            if "Relevant for Case Analysis" in df.columns:
                df = df[
                    (df["Relevant for Case Analysis"] == True) |
                    (df["Relevant for Case Analysis"] == "true") |
                    (df["Relevant for Case Analysis"] == "True") |
                    (df["Relevant for Case Analysis"] == 1)
                ]

            required_cols = ["Keywords", "Definition"]
            available_cols = [col for col in required_cols if col in df.columns]

            if available_cols:
                df = df[available_cols]
                if "Keywords" in df.columns:
                    df = df.rename(columns={"Keywords": "Theme"})
                df = df.reset_index(drop=True)
                return df

        except Exception as e2:
            print(f"Fallback also failed: {e2}")

        return pd.DataFrame(columns=["Theme", "Definition"])

def filter_themes_by_list(themes_list: list[str]) -> str:
    """
    Returns a markdown table (string) of Theme|Definition
    for those themes in themes_list, using the already‐loaded THEMES_TABLE_DF.
    """
    if not themes_list or THEMES_TABLE_DF.empty:
        return "No themes available."
    # fast in‐memory filter
    filtered_df = THEMES_TABLE_DF[THEMES_TABLE_DF["Theme"].isin(themes_list)]
    return format_themes_table(filtered_df)

def fetch_themes_list() -> list[str]:
    # just return the cached list
    return THEMES_TABLE_DF["Theme"].dropna().tolist()

def format_themes_table(df):
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
#THEMES_TABLE_DF  = pd.read_csv(CSV_PATH)
THEMES_TABLE_STR = format_themes_table(THEMES_TABLE_DF)

# Save to CSV (run once to recreate)
if __name__ == "__main__":
    THEMES_TABLE_DF.to_csv(CSV_PATH, index=False)
    print(f"Themes saved to {CSV_PATH}")
