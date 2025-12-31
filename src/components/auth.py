# components/auth.py
"""
Authentication and model selection functionality.
"""

import json
import logging
import os

from streamlit.runtime.secrets import secrets_singleton

logger = logging.getLogger(__name__)


def initialize_auth():
    """Initialize authentication session state and configure auth secrets from environment."""
    # Configure auth secrets from environment variables (works for both local .env and Azure)
    auth_redirect_uri = os.getenv("AUTH_REDIRECT_URI")
    auth_cookie_secret = os.getenv("AUTH_COOKIE_SECRET")
    auth_client_id = os.getenv("AUTH0_CLIENT_ID")
    auth_client_secret = os.getenv("AUTH0_CLIENT_SECRET")
    auth_server_metadata_url = os.getenv("AUTH0_SERVER_METADATA_URL")
    auth_client_kwargs = os.getenv("AUTH0_CLIENT_KWARGS", '{"prompt": "login"}')

    if all([auth_redirect_uri, auth_cookie_secret, auth_client_id, auth_client_secret, auth_server_metadata_url]):
        # Parse client_kwargs if it's a JSON string
        try:
            client_kwargs_dict = json.loads(auth_client_kwargs) if isinstance(auth_client_kwargs, str) else auth_client_kwargs
        except json.JSONDecodeError:
            logger.warning("Failed to parse AUTH0_CLIENT_KWARGS, using default")
            client_kwargs_dict = {"prompt": "login"}

        # Build auth config
        auth_config = {
            "auth": {
                "redirect_uri": auth_redirect_uri,
                "cookie_secret": auth_cookie_secret,
                "auth0": {
                    "client_id": auth_client_id,
                    "client_secret": auth_client_secret,
                    "server_metadata_url": auth_server_metadata_url,
                    "client_kwargs": client_kwargs_dict,
                },
            }
        }

        # Set secrets directly without merging - this initializes secrets from env vars
        secrets_singleton._secrets = auth_config
        logger.info("Auth secrets configured from environment variables")
    else:
        logger.warning("Auth environment variables not fully configured")
