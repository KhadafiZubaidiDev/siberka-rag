"""
rag/chain.py — RAG Chain dengan Gemini via Vertex AI
=====================================================
Menggunakan ConversationalRetrievalChain + streaming.
"""
from __future__ import annotations

import logging
from typing import Generator, Any

import vertexai
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.documents import Document
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import PromptTemplate

import config
from rag.vector_store import VectorStoreManager

logger = logging.getLogger(__name__)


# ── Prompt Templates ─────────────────────────────────────────────

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template("""
Berdasarkan riwayat percakapan dan pertanyaan lanjutan berikut,
formulasikan ulang pertanyaan lanjutan menjadi pertanyaan mandiri
yang bisa dipahami tanpa riwayat percakapan.

Riwayat Percakapan:
{chat_history}

Pertanyaan Lanjutan: {question}
Pertanyaan Mandiri:
""")

QA_PROMPT = PromptTemplate.from_template("""
Kamu adalah asisten AI cerdas bernama SiberkaRAG yang menjawab pertanyaan berdasarkan dokumen.

ATURAN PENTING:
1. Jawab HANYA berdasarkan konteks dokumen di bawah ini.
2. Jika informasi tidak tersedia dalam konteks, katakan: "Informasi ini tidak tersedia dalam dokumen yang diunggah."
3. Gunakan bahasa yang sama dengan pertanyaan (Indonesia atau Inggris).
4. Berikan jawaban terstruktur dengan poin-poin jika memungkinkan.
5. Selalu sebut sumber/halaman jika relevan.
6. Jangan mengarang atau menggunakan pengetahuan di luar dokumen.

Konteks Dokumen:
{context}

Pertanyaan: {question}

Jawaban yang informatif dan terstruktur:
""")


# ── RAG Chain Builder ─────────────────────────────────────────────

class RAGChain:
    """
    Encapsulates the ConversationalRetrievalChain untuk SiberkaRAG.

    Usage:
        chain = RAGChain(vsm)
        response = chain.ask("Apa itu machine learning?")
        print(response["answer"])
        print(response["source_documents"])
    """

    def __init__(self, vsm: VectorStoreManager, k: int = config.TOP_K_RETRIEVAL) -> None:
        self._vsm = vsm

        # Inisialisasi Vertex AI
        vertexai.init(
            project=config.GOOGLE_CLOUD_PROJECT,
            location=config.GOOGLE_CLOUD_REGION,
        )

        # LLM Gemini
        self._llm = ChatVertexAI(
            model_name=config.GEMINI_MODEL,
            project=config.GOOGLE_CLOUD_PROJECT,
            location=config.GOOGLE_CLOUD_REGION,
            temperature=config.GENERATION_CONFIG["temperature"],
            max_output_tokens=config.GENERATION_CONFIG["max_output_tokens"],
            top_p=config.GENERATION_CONFIG["top_p"],
            streaming=False,  # Kita handle streaming manual
        )

        # Memory — simpan 10 pertukaran terakhir
        self._memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

        # Retriever
        retriever = vsm.get_retriever(k=k)

        # Chain utama
        self._chain = ConversationalRetrievalChain.from_llm(
            llm=self._llm,
            retriever=retriever,
            memory=self._memory,
            condense_question_prompt=CONDENSE_QUESTION_PROMPT,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT},
            return_source_documents=True,
            verbose=False,
        )

        logger.info("RAGChain initialized with model '%s'.", config.GEMINI_MODEL)

    def ask(self, question: str) -> dict[str, Any]:
        """
        Jawab pertanyaan menggunakan RAG chain.

        Args:
            question: Pertanyaan dari pengguna.

        Returns:
            Dict berisi 'answer' (str) dan 'source_documents' (list[Document]).
        """
        logger.debug("RAGChain.ask: '%s'", question)
        result = self._chain.invoke({"question": question})
        return {
            "answer": result.get("answer", ""),
            "source_documents": result.get("source_documents", []),
        }

    def ask_with_sources(
        self,
        question: str,
    ) -> tuple[str, list[dict[str, Any]]]:
        """
        Jawab pertanyaan dan kembalikan sources yang terformat.

        Returns:
            Tuple (answer, sources) di mana sources adalah list dict
            berisi {filename, page, excerpt}.
        """
        result = self.ask(question)
        answer = result["answer"]

        # Format sumber
        sources: list[dict[str, Any]] = []
        seen_excerpts: set[str] = set()

        for doc in result["source_documents"]:
            excerpt = doc.page_content[:300].strip()
            if excerpt in seen_excerpts:
                continue
            seen_excerpts.add(excerpt)

            sources.append({
                "filename": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "—"),
                "chunk_index": doc.metadata.get("chunk_index", 0),
                "excerpt": excerpt,
            })

        return answer, sources

    def clear_memory(self) -> None:
        """Reset riwayat percakapan."""
        self._memory.clear()
        logger.info("Conversation memory cleared.")

    def get_chat_history(self) -> list[tuple[str, str]]:
        """Kembalikan riwayat percakapan sebagai list (human, ai) tuples."""
        messages = self._memory.chat_memory.messages
        history: list[tuple[str, str]] = []
        for i in range(0, len(messages) - 1, 2):
            human = getattr(messages[i], "content", "")
            ai = getattr(messages[i + 1], "content", "") if i + 1 < len(messages) else ""
            history.append((human, ai))
        return history
