"""
Central config. Reads settings from the .env file once, so every other
module imports the same values.

Beginner notes:
- `load_dotenv()` reads the .env file and puts the values into the
  environment so `os.getenv(...)` can find them.
- We DON'T crash if the key is missing. Instead `HAS_KEY` is False and the
  API returns a clear message. Crashing on import is a common cause of the
  server "not running" -> "unable to fetch" in the browser.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Folder that contains this file (backend/)
BASE_DIR = Path(__file__).resolve().parent

# Load backend/.env into the environment (no error if the file is absent)
load_dotenv(BASE_DIR / ".env")

# --- OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini").strip()
EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small").strip()

# True only if a real-looking key is present
HAS_KEY = OPENAI_API_KEY.startswith("sk-")

# --- Paths ---
DATA_DIR = BASE_DIR / "data"            # source documents (.md / .txt)
CHROMA_DIR = BASE_DIR / "chroma_store"  # persistent vector store on disk
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# --- Retrieval / chunking ---
COLLECTION_NAME = "medical_docs"
CHUNK_SIZE = 900          # characters per chunk (simple + reliable)
CHUNK_OVERLAP = 150       # characters of overlap between chunks
TOP_K = 4                 # how many chunks to retrieve per question
