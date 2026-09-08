"""
config.py — Konfigurasi terpusat SiberkaRAG
============================================
Semua nilai bisa di-override via environment variables atau file .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env jika ada
load_dotenv()

# ── Google Cloud ──────────────────────────────────────────────────
GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
GOOGLE_CLOUD_REGION: str  = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# ── Model Names ───────────────────────────────────────────────────
GEMINI_MODEL: str     = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
EMBEDDING_MODEL: str  = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

# ── ChromaDB ──────────────────────────────────────────────────────
CHROMA_PERSIST_DIR: str       = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME: str   = os.getenv("CHROMA_COLLECTION_NAME", "siberka_docs")

# ── RAG Parameters ────────────────────────────────────────────────
CHUNK_SIZE: int      = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP: int   = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))

# ── Auth & User Management ────────────────────────────────────────
DB_PATH: str                 = os.getenv("DB_PATH", "./data/siberka.db")
ADMIN_USERNAME: str          = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD: str  = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@1234")
DEFAULT_DOC_QUOTA: int       = int(os.getenv("DEFAULT_DOC_QUOTA", "20"))
ALLOW_REGISTER: bool         = os.getenv("ALLOW_REGISTER", "false").lower() == "true"

# ── App ───────────────────────────────────────────────────────────
APP_TITLE: str = os.getenv("APP_TITLE", "SiberkaRAG")
UPLOAD_DIR: Path = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
Path("./data").mkdir(exist_ok=True)

# Ekstensi file yang didukung
SUPPORTED_EXTENSIONS: list[str] = [".pdf", ".txt", ".docx"]

# ── Generation Config ─────────────────────────────────────────────
GENERATION_CONFIG = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

# System prompt untuk RAG
RAG_SYSTEM_PROMPT = """Kamu adalah asisten AI yang cerdas dan membantu bernama SiberkaRAG.
Tugasmu adalah menjawab pertanyaan pengguna berdasarkan dokumen yang telah diunggah.

Panduan:
1. Jawab HANYA berdasarkan konteks dokumen yang diberikan.
2. Jika informasi tidak ada di dokumen, katakan dengan jujur.
3. Sertakan referensi ke bagian dokumen yang relevan.
4. Gunakan bahasa yang sama dengan pertanyaan pengguna (Indonesia atau Inggris).
5. Berikan jawaban yang terstruktur, jelas, dan informatif.
6. Jika ada beberapa sumber, sintesiskan informasi dari semua sumber.

Konteks Dokumen:
{context}

Riwayat Percakapan:
{chat_history}
"""
