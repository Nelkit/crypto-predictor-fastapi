import os
from pathlib import Path

BASE_API_URL = "https://api.coingecko.com/api/v3"

def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key:
            os.environ.setdefault(key, value)


# Load environment variables from the project-level .env file.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
_load_env_file(PROJECT_ROOT / ".env")

API_KEY = os.getenv("COINGECKO_API_KEY")