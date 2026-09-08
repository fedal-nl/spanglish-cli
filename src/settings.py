import os

from dotenv import load_dotenv

load_dotenv()

SPANGLISH_API_URL = os.getenv(
    "SPANGLISH_API_URL", "http://127.0.0.1:8000/api/v1/spanglish"
).rstrip("/")
API_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "15"))
