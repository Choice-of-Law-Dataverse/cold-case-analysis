import pandas as pd
from pyairtable import Api
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_CONCEPTS_TABLE

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
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_CONCEPTS_TABLE)
    records = table.all()

    if not records:
        return pd.DataFrame(columns=["Theme", "Definition"])

    df = pd.json_normalize([record["fields"] for record in records])
    df = remove_fields_prefix(df)
    df = process_list_like_values(df)
    df = df[df["Relevant for Case Analysis"] == True]
    df = df[["Keywords", "Definition"]]
    df = df.rename(columns={"Keywords": "Theme"})
    df = df.reset_index(drop=True)
    return df

def fetch_themes_list():
    df = fetch_themes_dataframe()
    return df["Theme"].tolist()

def format_themes_table(df):
    if df.empty:
        return "No themes available."
    table_str = "| Theme | Definition |\n"
    table_str += "|-------|------------|\n"
    for _, row in df.iterrows():
        theme = str(row['Theme']).replace("|", "\\|")
        definition = str(row['Definition']).replace("|", "\\|")
        table_str += f"| {theme} | {definition} |\n"
    return table_str

THEMES_TABLE_DF = fetch_themes_dataframe()
THEMES_TABLE_STR = format_themes_table(THEMES_TABLE_DF)