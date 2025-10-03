# filepath: /home/simon/dev/cold-case-analysis/cold_case_analyzer_agent/latam_case_analysis/pdf_extractor.py
#!/usr/bin/env python3
"""
Downloads PDFs from Airtable for records in 'Court Decisions' table where
'Venabled' region is 'South & Latin America'. Saves PDFs to the 'pdfs' directory.
"""

import os

import requests

# Load Airtable API key from environment variable
API_KEY = os.getenv("AIRTABLE_API_KEY")
if not API_KEY:
    raise ValueError("Please set the AIRTABLE_API_KEY environment variable")

# Airtable identifiers
BASE_ID = "appz9Ei9mu9NIGmbK"
TABLE_ID = "tbl8hWTY8ArXzJCr2"  # Court Decisions
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "pdfs")

# Ensure output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Common headers for Airtable API
HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

# Filter formula to only include South & Latin America records
FILTER_FORMULA = "{Region (from Jurisdictions)} = 'South & Latin America'"


def fetch_records(offset=None):
    """
    Fetch a page of records from Airtable, applying the region filter and pagination.
    Returns a tuple of (records_list, next_offset).
    """
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    params = {
        "filterByFormula": FILTER_FORMULA,
        "pageSize": 100
    }
    if offset:
        params["offset"] = offset
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("records", []), data.get("offset")


def download_attachment(record_id, attachment):
    """
    Download a single attachment to the OUTPUT_DIR, prefixing with the record ID.
    """
    url = attachment["url"]
    filename = attachment.get("filename") or f"{record_id}.pdf"
    save_path = os.path.join(OUTPUT_DIR, f"{record_id}_{filename}")
    print(f"Downloading {filename} for record {record_id}...")
    with requests.get(url, headers=HEADERS, stream=True) as r:
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def main():
    offset = None
    while True:
        records, offset = fetch_records(offset)
        for rec in records:
            attachments = rec.get("fields", {}).get("Official Source (PDF)", []) or []
            for att in attachments:
                download_attachment(rec["id"], att)
        if not offset:
            break


if __name__ == "__main__":
    main()
