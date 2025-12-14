"""
Configuration loader for the voice-controlled emote system.

Loads config.json and provides defaults for missing values.
"""

import json
import os

# Default configuration (used when config.json is missing or incomplete)
DEFAULTS = {
    "toggle_word": "toggle",
    "keyword_triggers": {
        "cooldown": 3.0,
        "groups": [
            {"triggers": ["yes", "yeah", "yep", "yup"], "emotes": ["yes"]},
            {"triggers": ["no", "nope", "nah"], "emotes": ["no", "no2"]},
        ],
    },
}


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base, returning a new dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str = None) -> dict:
    """
    Load configuration from JSON file, falling back to defaults.

    Args:
        path: Path to config.json. If None, looks in same directory as this module.

    Returns:
        Configuration dict with all values populated (defaults + overrides).
    """
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "config.json")

    config = DEFAULTS.copy()

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            config = deep_merge(DEFAULTS, user_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {path}: {e}")
            print("Using default configuration.")
    else:
        print(f"Config file not found: {path}")
        print("Using default configuration.")

    return config


def get_keyword_config(config: dict) -> dict:
    """Extract keyword triggers config."""
    return config.get("keyword_triggers", DEFAULTS["keyword_triggers"])


if __name__ == "__main__":
    # Test loading
    cfg = load_config()
    print("Loaded configuration:")
    print(json.dumps(cfg, indent=2))
