import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SPANGLISH_API_URL = os.getenv(
    "SPANGLISH_API_URL", "http://127.0.0.1:8000/api/v1/spanglish"
).rstrip("/")
API_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "15"))
R2D2_API_URL = SPANGLISH_API_URL.removesuffix("/spanglish")
R2D2_SERVER_URL = R2D2_API_URL.removesuffix("/api/v1")
TOKEN_STORE_PATH = Path(
    os.getenv("R2D2_TOKEN_STORE_PATH", "~/.config/spanglish/tokens.json")
).expanduser()
