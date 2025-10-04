import json
import logging

logger = logging.getLogger(__name__)


def print_state(header: str, state_dict: dict) -> None:
    """Log a header and pretty-printed JSON of a state dictionary at debug level."""
    logger.debug("[DEBUG] %s:", header)
    logger.debug("%s", json.dumps(state_dict, indent=2, default=str))
