# Azure Blob Storage Integration for PDF Uploads

## Overview

The CoLD Case Analyzer now supports automatic upload of PDF files to Azure Blob Storage. When a user uploads a PDF file through the Streamlit interface, the system:

1. Generates a unique UUID for the file
2. Uploads the PDF to Azure Blob Storage (if configured)
3. Stores the Azure URL, UUID, and filename in the analysis state
4. Saves this metadata to the database as part of the analysis results

## Authentication Methods

The system supports two authentication methods:

### Option 1: Managed Identity (Recommended for Azure Container Apps)

Uses Azure's built-in Managed Identity for secure, credential-free authentication.

**Environment Variables:**
```bash
AZURE_STORAGE_ACCOUNT_NAME="your_storage_account_name"
AZURE_STORAGE_CONTAINER_NAME="case-pdfs"

# Optional: For User-assigned Managed Identity
# AZURE_CLIENT_ID="your-user-assigned-identity-client-id"
```

**Setup Steps:**
1. Enable Managed Identity on your Container App (Settings → Identity)
2. Assign "Storage Blob Data Contributor" role to the identity
3. Configure environment variables (no secrets needed!)

**Benefits:**
- No connection strings or keys to manage
- Automatic credential rotation
- Works seamlessly with Azure Container Apps
- Supports both System-assigned and User-assigned identities

### Option 2: Connection String (Traditional)

Uses storage account connection string with access keys.

**Environment Variables:**
```bash
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=your_account;AccountKey=your_key;EndpointSuffix=core.windows.net"
AZURE_STORAGE_CONTAINER_NAME="case-pdfs"
```

**Getting Connection String:**
1. Create an Azure Storage Account in the Azure Portal
2. Create a container (e.g., `case-pdfs`) in the storage account
3. Go to "Access keys" under the storage account settings
4. Copy the connection string

## Configuration

### For Azure Container Apps (Managed Identity)

1. **Enable Managed Identity:**
   - Navigate to your Container App in Azure Portal
   - Settings → Identity → System assigned
   - Toggle Status to "On" and Save

2. **Grant Storage Access:**
   - Navigate to your Storage Account
   - Access Control (IAM) → Add role assignment
   - Select "Storage Blob Data Contributor"
   - Assign to your Container App's Managed Identity

3. **Configure Environment Variables:**
   - In Container App: Settings → Environment variables
   - Add: `AZURE_STORAGE_ACCOUNT_NAME` = your storage account name
   - Add: `AZURE_STORAGE_CONTAINER_NAME` = `case-pdfs`
   - (Remove `AZURE_STORAGE_CONNECTION_STRING` if present)

### For Local Development

**With Managed Identity:**
1. Install Azure CLI: `az login`
2. Grant your user account "Storage Blob Data Contributor" role on the storage account
3. Set environment variables:
   ```bash
   export AZURE_STORAGE_ACCOUNT_NAME="your_account_name"
   export AZURE_STORAGE_CONTAINER_NAME="case-pdfs"
   ```
4. Run your app - `DefaultAzureCredential` will use Azure CLI credentials

**With Connection String:**
1. Set environment variables in `.env`:
   ```bash
   AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=..."
   AZURE_STORAGE_CONTAINER_NAME="case-pdfs"
   ```

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

Uploads a PDF file to Azure Blob Storage using configured authentication method.

**Parameters:**
- `pdf_file` (file-like): The PDF file object from Streamlit's file uploader
- `original_filename` (str, optional): The original filename

**Returns:**
- `dict` with keys `uuid`, `url`, `filename` on success
- `None` if Azure is not configured or upload fails

**Authentication:**
- Automatically uses Managed Identity if `AZURE_STORAGE_ACCOUNT_NAME` is set
- Falls back to connection string if `AZURE_STORAGE_CONNECTION_STRING` is set
- Works with both System-assigned and User-assigned Managed Identities

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
