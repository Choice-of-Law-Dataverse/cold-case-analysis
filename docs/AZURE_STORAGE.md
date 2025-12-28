# Azure Blob Storage Integration for PDF Uploads

## Overview

The CoLD Case Analyzer now supports automatic upload of PDF files to Azure Blob Storage. When a user uploads a PDF file through the Streamlit interface, the system:

1. Generates a unique UUID for the file
2. Uploads the PDF to Azure Blob Storage (if configured)
3. Stores the Azure URL, UUID, and filename in the analysis state
4. Saves this metadata to the database as part of the analysis results

## Configuration

To enable Azure Blob Storage integration, set the following environment variables in your `.env` file:

```bash
# Azure Blob Storage connection string
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=your_account;AccountKey=your_key;EndpointSuffix=core.windows.net"

# Azure Blob Storage container name for PDFs
AZURE_STORAGE_CONTAINER_NAME="case-pdfs"
```

### Getting Your Azure Credentials

1. Create an Azure Storage Account in the Azure Portal
2. Create a container (e.g., `case-pdfs`) in the storage account
3. Go to "Access keys" under the storage account settings
4. Copy the connection string

## Behavior

### When Azure is Configured

- PDFs are automatically uploaded to Azure Blob Storage
- The system generates a UUID for each file (e.g., `a1b2c3d4-5678-90ab-cdef-1234567890ab.pdf`)
- The blob URL is stored in the analysis state
- The URL is included in the database save

### When Azure is Not Configured

- PDF text extraction still works normally
- No upload occurs (logged as warning)
- The application continues to function without Azure storage
- PDF metadata fields are not added to the state

## Database Schema

The PDF metadata is stored in the `suggestions_case_analyzer` table's `data` JSONB column:

```json
{
  "case_citation": "...",
  "username": "...",
  "pdf_url": "https://accountname.blob.core.windows.net/case-pdfs/uuid.pdf",
  "pdf_uuid": "uuid-string",
  "pdf_filename": "original_filename.pdf",
  ...
}
```

## API Reference

### `upload_pdf_to_azure(pdf_file, original_filename)`

Uploads a PDF file to Azure Blob Storage.

**Parameters:**
- `pdf_file` (file-like): The PDF file object from Streamlit's file uploader
- `original_filename` (str, optional): The original filename

**Returns:**
- `dict` with keys `uuid`, `url`, `filename` on success
- `None` if Azure is not configured or upload fails

**Example:**
```python
from utils.azure_storage import upload_pdf_to_azure

result = upload_pdf_to_azure(pdf_file, "case_decision.pdf")
if result:
    print(f"Uploaded to {result['url']}")
```

### `is_azure_storage_configured()`

Checks if Azure Storage is properly configured.

**Returns:**
- `bool`: True if both connection string and container name are set

## Testing

Run the test suite:

```bash
pytest src/tests/test_azure_storage.py -v
```

Run the integration test:

```bash
python src/tests/test_pdf_metadata_integration.py
```

Run the demo:

```bash
PYTHONPATH=src python demo_pdf_flow.py
```

## Security Considerations

- The Azure connection string contains sensitive credentials - never commit it to version control
- Use Azure's SAS (Shared Access Signature) tokens for fine-grained access control if needed
- Consider implementing blob lifecycle policies to manage storage costs
- The uploaded PDFs should be stored in a private container with appropriate access controls

## Implementation Details

### Files Modified

- `pyproject.toml` - Added `azure-storage-blob>=12.24.0` dependency
- `.env.example` - Added Azure configuration template
- `src/utils/azure_storage.py` - New utility module for Azure operations
- `src/components/input_handler.py` - Updated to upload PDFs and store metadata
- `src/utils/state_manager.py` - Updated to include PDF metadata in state
- `src/components/database.py` - No changes needed (already serializes entire state)

### Files Added

- `src/tests/test_azure_storage.py` - Comprehensive test suite
- `src/tests/test_pdf_metadata_integration.py` - Integration test
- `demo_pdf_flow.py` - Demonstration script

## Troubleshooting

### "Module 'azure' not found"

Install dependencies:
```bash
pip install -e .
```

### "Failed to upload PDF to Azure Blob Storage"

Check your configuration:
1. Verify `AZURE_STORAGE_CONNECTION_STRING` is correct
2. Verify `AZURE_STORAGE_CONTAINER_NAME` exists in your storage account
3. Check network connectivity to Azure
4. Review application logs for detailed error messages

### PDF text extraction works but no URL in database

This is expected if Azure Storage is not configured. The system gracefully degrades to text-only processing.
