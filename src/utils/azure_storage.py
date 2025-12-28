"""
Azure Blob Storage utilities for PDF uploads.

Supports both connection string and Managed Identity authentication.
"""

import logging
import os
import uuid
from typing import BinaryIO, Protocol

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)


class SupportsRead(Protocol):
    def read(self, size: int | None = None) -> bytes:
        ...


def is_azure_storage_configured() -> bool:
    """
    Check if Azure Storage is properly configured.

    Returns:
        bool: True if either connection string or account name is configured
    """
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    # Need container name and either connection string or account name
    return bool(container_name and (connection_string or account_name))


def _get_blob_service_client() -> BlobServiceClient:
    """
    Create BlobServiceClient using connection string or Managed Identity.

    Returns:
        BlobServiceClient: Configured blob service client

    Raises:
        ValueError: If Azure Storage is not properly configured
    """
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")

    if connection_string:
        # Use connection string authentication
        logger.debug("Using connection string for Azure authentication")
        return BlobServiceClient.from_connection_string(connection_string)
    elif account_name:
        # Use Managed Identity / DefaultAzureCredential
        logger.debug("Using Managed Identity (DefaultAzureCredential) for Azure authentication")
        account_url = f"https://{account_name}.blob.core.windows.net"
        credential = DefaultAzureCredential()
        return BlobServiceClient(account_url, credential=credential)
    else:
        raise ValueError("Azure Storage not configured: need AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_NAME")


def upload_pdf_to_azure(pdf_file: SupportsRead | BinaryIO, original_filename: str | None = None) -> dict | None:
    """
    Upload a PDF file to Azure Blob Storage with a UUID.

    Supports both connection string and Managed Identity authentication.

    Args:
        pdf_file: File-like object (e.g., from Streamlit's file_uploader)
        original_filename: Original name of the file (optional)

    Returns:
        dict with keys 'uuid', 'url', 'filename' if successful, None if Azure is not configured or upload fails
    """
    if not is_azure_storage_configured():
        logger.warning("Azure Storage not configured. Skipping PDF upload.")
        return None

    try:
        container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

        # Generate UUID for the file
        file_uuid = str(uuid.uuid4())
        blob_name = f"{file_uuid}.pdf"

        # Read the file content
        file_content = pdf_file.read()

        # Reset the file pointer if possible (for later text extraction)
        if hasattr(pdf_file, "seek"):
            pdf_file.seek(0)

        # Create blob service client and upload
        blob_service_client = _get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        blob_client.upload_blob(file_content, overwrite=True, content_type="application/pdf")

        # Construct the URL
        blob_url = blob_client.url

        logger.info(f"Successfully uploaded PDF with UUID {file_uuid} to Azure Blob Storage")

        return {
            "uuid": file_uuid,
            "url": blob_url,
            "filename": original_filename or "uploaded.pdf",
        }

    except Exception as e:
        logger.error(f"Failed to upload PDF to Azure Blob Storage: {e}", exc_info=True)
        return None
