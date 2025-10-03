import json


def print_state(header: str, state_dict: dict) -> None:
    """Print a header and pretty-printed JSON of a state dictionary."""
    print(f"[DEBUG] {header}:")
    print(json.dumps(state_dict, indent=2, default=str))
