"""
rag/vector_store.py — ChromaDB Vector Store Manager
=====================================================
Persistent ChromaDB untuk menyimpan dan mencari dokumen.
Mendukung isolasi per-user via collection name unik.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, TYPE_CHECKING

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

if TYPE_CHECKING:
    from auth.models import User

import config
from rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)


# ── Data class untuk info dokumen ─────────────────────────────────

@dataclass
class DocumentInfo:
    """Metadata ringkas untuk satu dokumen."""
    filename: str
    file_hash: str
    chunk_count: int
    total_chars: int
    total_pages: int


# ── Vector Store Manager ─────────────────────────────────────────

class VectorStoreManager:
    """
    Mengelola ChromaDB persistent collection.

    Usage:
        vsm = VectorStoreManager()
        vsm.add_documents(chunks, doc_info)
        results = vsm.similarity_search("query", k=5)
        vsm.delete_document("filename.pdf")
    """

    def __init__(self, collection_name: str | None = None) -> None:
        self._collection_name = collection_name or config.CHROMA_COLLECTION_NAME
        self._client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self._embeddings = get_embeddings()
        self._vectorstore: Chroma | None = None
        self._load_or_create()

    # ── Private ──────────────────────────────────────────────────

    def _load_or_create(self) -> None:
        """Muat koleksi yang ada atau buat baru."""
        self._vectorstore = Chroma(
            client=self._client,
            collection_name=self._collection_name,
            embedding_function=self._embeddings,
        )
        count = self._vectorstore._collection.count()
        logger.info("ChromaDB loaded. Collection '%s' has %d vectors.",
                    self._collection_name, count)


    # ── Public ───────────────────────────────────────────────────

    def add_documents(
        self,
        chunks: list[Document],
        doc_info: DocumentInfo,
    ) -> int:
        """
        Tambahkan chunks ke vector store.

        Args:
            chunks:   List LangChain Documents (sudah di-split).
            doc_info: Metadata dokumen untuk disimpan.

        Returns:
            Jumlah chunks yang berhasil ditambahkan.
        """
        if not chunks:
            return 0

        # Tambahkan metadata doc_info ke setiap chunk
        for chunk in chunks:
            chunk.metadata.update({
                "doc_filename": doc_info.filename,
                "doc_hash": doc_info.file_hash,
                "doc_total_pages": doc_info.total_pages,
                "doc_total_chars": doc_info.total_chars,
            })

        self._vectorstore.add_documents(chunks)
        logger.info("Added %d chunks for '%s'.", len(chunks), doc_info.filename)
        return len(chunks)

    def similarity_search(
        self,
        query: str,
        k: int = config.TOP_K_RETRIEVAL,
        filter_filename: str | None = None,
    ) -> list[Document]:
        """
        Cari dokumen yang paling relevan secara semantik.

        Args:
            query:           Teks query dari pengguna.
            k:               Jumlah hasil teratas yang dikembalikan.
            filter_filename: Opsional — filter hanya dari file tertentu.

        Returns:
            List Documents yang paling relevan.
        """
        where: dict[str, Any] | None = None
        if filter_filename:
            where = {"doc_filename": filter_filename}

        results = self._vectorstore.similarity_search(
            query, k=k, filter=where
        )
        logger.debug("similarity_search('%s'): %d results.", query, len(results))
        return results

    def similarity_search_with_score(
        self,
        query: str,
        k: int = config.TOP_K_RETRIEVAL,
    ) -> list[tuple[Document, float]]:
        """Similarity search dengan skor relevansi (0–1)."""
        return self._vectorstore.similarity_search_with_relevance_scores(query, k=k)

    def delete_document(self, filename: str) -> int:
        """
        Hapus semua chunks milik satu dokumen.

        Args:
            filename: Nama file yang akan dihapus.

        Returns:
            Jumlah chunks yang dihapus.
        """
        collection = self._vectorstore._collection
        results = collection.get(where={"doc_filename": filename})
        ids = results.get("ids", [])
        if ids:
            collection.delete(ids=ids)
            logger.info("Deleted %d chunks for '%s'.", len(ids), filename)
        return len(ids)

    def list_documents(self) -> list[DocumentInfo]:
        """
        Kembalikan daftar dokumen unik yang tersimpan.

        Returns:
            List DocumentInfo, satu entry per dokumen.
        """
        collection = self._vectorstore._collection
        if collection.count() == 0:
            return []

        results = collection.get(include=["metadatas"])
        seen: dict[str, DocumentInfo] = {}

        for meta in results.get("metadatas", []):
            fname = meta.get("doc_filename", "unknown")
            if fname not in seen:
                seen[fname] = DocumentInfo(
                    filename=fname,
                    file_hash=meta.get("doc_hash", ""),
                    chunk_count=0,
                    total_chars=meta.get("doc_total_chars", 0),
                    total_pages=meta.get("doc_total_pages", 0),
                )
            seen[fname].chunk_count += 1

        return list(seen.values())

    def get_retriever(self, k: int = config.TOP_K_RETRIEVAL):
        """Kembalikan LangChain retriever untuk digunakan di chain."""
        return self._vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

    def collection_count(self) -> int:
        """Total jumlah vectors dalam koleksi."""
        return self._vectorstore._collection.count()

    def clear_all(self) -> None:
        """Hapus SEMUA dokumen dari koleksi. Hati-hati!"""
        self._client.delete_collection(self._collection_name)
        self._load_or_create()
        logger.warning("All documents cleared from collection '%s'.", self._collection_name)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PER-USER FACTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@lru_cache(maxsize=32)
def _cached_vsm(collection_name: str) -> VectorStoreManager:
    """Cache VectorStoreManager per collection name."""
    return VectorStoreManager(collection_name=collection_name)


def get_vsm_for_user(user: "User") -> VectorStoreManager:
    """
    Kembalikan VectorStoreManager yang terisolasi untuk satu user.

    Setiap user mendapatkan ChromaDB collection sendiri berdasarkan
    `user.collection_name` sehingga dokumen antar-user tidak bercampur.

    Args:
        user: User object dari auth.models.

    Returns:
        VectorStoreManager instance untuk user tersebut.
    """
    return _cached_vsm(user.collection_name)
