import os

from dotenv import load_dotenv


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()


def require_groq_api_key():
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing. Add it to .env or your environment.")
    return GROQ_API_KEY
