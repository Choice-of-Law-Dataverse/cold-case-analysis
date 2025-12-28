"""
Azure Blob Storage utilities for PDF uploads.
"""

import logging
import os
import uuid
from typing import BinaryIO, Protocol

from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)


class SupportsRead(Protocol):
    def read(self, size: int | None = None) -> bytes:
        ...


def is_azure_storage_configured() -> bool:
    """
    Check if Azure Storage is properly configured.

    Returns:
        bool: True if both connection string and container name are set
    """
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    return bool(connection_string and container_name)


def upload_pdf_to_azure(pdf_file: SupportsRead | BinaryIO, original_filename: str | None = None) -> dict | None:
    """
    Upload a PDF file to Azure Blob Storage with a UUID.

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
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
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
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
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
