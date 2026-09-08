"""
rag/embeddings.py — Vertex AI Embeddings wrapper untuk LangChain
================================================================
Menggunakan model text-embedding-004 via langchain-google-vertexai.
"""
from __future__ import annotations

import logging
from functools import lru_cache

import vertexai
from langchain_google_vertexai import VertexAIEmbeddings

import config

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embeddings() -> VertexAIEmbeddings:
    """
    Inisialisasi dan kembalikan singleton VertexAIEmbeddings.

    Menggunakan @lru_cache sehingga koneksi hanya dibuat sekali
    per sesi Streamlit.

    Returns:
        VertexAIEmbeddings instance siap pakai.
    """
    logger.info(
        "Initializing Vertex AI Embeddings: project=%s, region=%s, model=%s",
        config.GOOGLE_CLOUD_PROJECT,
        config.GOOGLE_CLOUD_REGION,
        config.EMBEDDING_MODEL,
    )

    vertexai.init(
        project=config.GOOGLE_CLOUD_PROJECT,
        location=config.GOOGLE_CLOUD_REGION,
    )

    embeddings = VertexAIEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        project=config.GOOGLE_CLOUD_PROJECT,
        location=config.GOOGLE_CLOUD_REGION,
    )

    logger.info("Vertex AI Embeddings ready.")
    return embeddings
