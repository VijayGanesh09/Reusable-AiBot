
import os
from pathlib import Path
from dotenv import load_dotenv


# =================================
# BACKEND DIRECTORY
# =================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load backend/.env
load_dotenv(BASE_DIR / ".env")


# =================================
# STORAGE CONFIGURATION
# =================================

UPLOAD_FOLDER = os.getenv(
    "UPLOAD_FOLDER",
    str(BASE_DIR / "uploads")
)

CHROMA_DB_PATH = os.getenv(
    "CHROMA_DB_PATH",
    str(BASE_DIR / "chroma_db")
)

KNOWLEDGE_BASE_FOLDER = os.getenv(
    "KNOWLEDGE_BASE_FOLDER",
    str(BASE_DIR / "knowledge_base")
)


# =================================
# EMBEDDING MODEL CONFIGURATION
# =================================

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2"
)


# =================================
# LLM CONFIGURATION
# =================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "openai/gpt-oss-20b"
)


# =================================
# TEXT CHUNK CONFIGURATION
# =================================

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

if CHUNK_SIZE <= 0:
    raise ValueError("CHUNK_SIZE must be greater than zero")

if CHUNK_OVERLAP < 0 or CHUNK_OVERLAP >= CHUNK_SIZE:
    raise ValueError(
        "CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE"
    )


# =================================
# RETRIEVAL CONFIGURATION
# =================================

TOP_K = int(os.getenv("TOP_K", "4"))

if TOP_K <= 0:
    raise ValueError("TOP_K must be greater than zero")


# =================================
# CREATE REQUIRED DIRECTORIES
# =================================

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)
Path(KNOWLEDGE_BASE_FOLDER).mkdir(parents=True, exist_ok=True)
