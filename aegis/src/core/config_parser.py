from pathlib import Path
from typing import Any

import tomllib


def parse_toml_config(file_path: str | Path) -> dict[str, Any]:
    """Reads a TOML file and returns a raw dictionary without validation."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path.resolve()}")

    with path.open("rb") as f:
        return tomllib.load(f)


config = parse_toml_config("./aegis.toml")
