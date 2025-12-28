"""
Tests for Azure Blob Storage integration.
"""

import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src directory to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from utils.azure_storage import is_azure_storage_configured, upload_pdf_to_azure  # noqa: E402


class TestAzureStorageConfiguration:
    """Tests for Azure Storage configuration checking."""

    def test_is_configured_with_both_values(self, monkeypatch):
        """Test that is_azure_storage_configured returns True when both values are set."""
        monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "test_connection_string")
        monkeypatch.setenv("AZURE_STORAGE_CONTAINER_NAME", "test_container")
        assert is_azure_storage_configured() is True

    def test_is_not_configured_missing_connection_string(self, monkeypatch):
        """Test that is_azure_storage_configured returns False when connection string is missing."""
        monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)
        monkeypatch.setenv("AZURE_STORAGE_CONTAINER_NAME", "test_container")
        assert is_azure_storage_configured() is False

    def test_is_not_configured_missing_container_name(self, monkeypatch):
        """Test that is_azure_storage_configured returns False when container name is missing."""
        monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "test_connection_string")
        monkeypatch.delenv("AZURE_STORAGE_CONTAINER_NAME", raising=False)
        assert is_azure_storage_configured() is False

    def test_is_not_configured_both_missing(self, monkeypatch):
        """Test that is_azure_storage_configured returns False when both values are missing."""
        monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)
        monkeypatch.delenv("AZURE_STORAGE_CONTAINER_NAME", raising=False)
        assert is_azure_storage_configured() is False


class TestUploadPdfToAzure:
    """Tests for PDF upload to Azure Blob Storage."""

    def test_upload_returns_none_when_not_configured(self, monkeypatch):
        """Test that upload returns None when Azure is not configured."""
        monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)
        monkeypatch.delenv("AZURE_STORAGE_CONTAINER_NAME", raising=False)

        pdf_file = BytesIO(b"fake pdf content")
        result = upload_pdf_to_azure(pdf_file, "test.pdf")
        assert result is None

    @patch("utils.azure_storage.BlobServiceClient")
    def test_upload_success(self, mock_blob_service, monkeypatch):
        """Test successful PDF upload to Azure."""
        monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "test_connection_string")
        monkeypatch.setenv("AZURE_STORAGE_CONTAINER_NAME", "test_container")

        # Setup mock
        mock_blob_client = MagicMock()
        mock_blob_client.url = "https://test.blob.core.windows.net/test_container/test-uuid.pdf"
        mock_blob_service.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

        pdf_file = BytesIO(b"fake pdf content")
        result = upload_pdf_to_azure(pdf_file, "test.pdf")

        assert result is not None
        assert "uuid" in result
        assert "url" in result
        assert "filename" in result
        assert result["filename"] == "test.pdf"
        assert result["url"] == "https://test.blob.core.windows.net/test_container/test-uuid.pdf"

        # Verify blob was uploaded
        mock_blob_client.upload_blob.assert_called_once()

    @patch("utils.azure_storage.BlobServiceClient")
    def test_upload_resets_file_pointer(self, mock_blob_service, monkeypatch):
        """Test that file pointer is reset after reading for upload."""
        monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "test_connection_string")
        monkeypatch.setenv("AZURE_STORAGE_CONTAINER_NAME", "test_container")

        # Setup mock
        mock_blob_client = MagicMock()
        mock_blob_client.url = "https://test.blob.core.windows.net/test_container/test-uuid.pdf"
        mock_blob_service.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

        pdf_file = BytesIO(b"fake pdf content")
        initial_position = pdf_file.tell()

        result = upload_pdf_to_azure(pdf_file, "test.pdf")

        # File pointer should be reset to allow text extraction
        assert pdf_file.tell() == initial_position
        assert result is not None

    @patch("utils.azure_storage.BlobServiceClient")
    def test_upload_handles_error(self, mock_blob_service, monkeypatch):
        """Test that upload handles errors gracefully."""
        monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "test_connection_string")
        monkeypatch.setenv("AZURE_STORAGE_CONTAINER_NAME", "test_container")

        # Setup mock to raise exception
        mock_blob_service.from_connection_string.side_effect = Exception("Upload failed")

        pdf_file = BytesIO(b"fake pdf content")
        result = upload_pdf_to_azure(pdf_file, "test.pdf")

        assert result is None

    @patch("utils.azure_storage.BlobServiceClient")
    def test_upload_without_filename(self, mock_blob_service, monkeypatch):
        """Test upload without providing original filename."""
        monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "test_connection_string")
        monkeypatch.setenv("AZURE_STORAGE_CONTAINER_NAME", "test_container")

        # Setup mock
        mock_blob_client = MagicMock()
        mock_blob_client.url = "https://test.blob.core.windows.net/test_container/test-uuid.pdf"
        mock_blob_service.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

        pdf_file = BytesIO(b"fake pdf content")
        result = upload_pdf_to_azure(pdf_file)

        assert result is not None
        assert result["filename"] == "uploaded.pdf"
