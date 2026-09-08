# 🧠 SiberkaRAG

**NotebookLM-style RAG application** powered by Google Vertex AI (Gemini), ChromaDB, dan Streamlit dengan tampilan glass morphism.

---

## ✨ Fitur

| Fitur | Deskripsi |
|---|---|
| 📄 Multi-format Upload | PDF, TXT, DOCX |
| 🔍 Semantic Search | Vertex AI `text-embedding-004` |
| 💬 Conversational QA | Chat history-aware dengan Gemini 1.5 Flash |
| 📎 Citation Sources | Sumber dokumen + nomor halaman |
| 🎨 Glass Morphism UI | Dark gradient + frosted glass cards |
| 📊 Document Management | Upload, lihat, hapus dokumen |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
cd siberka-rag
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Konfigurasi

```bash
cp .env.example .env
```

Edit `.env`:
```env
GOOGLE_CLOUD_PROJECT=your-actual-project-id
GOOGLE_CLOUD_REGION=us-central1
```

### 3. Google Cloud Authentication

```bash
# Install Google Cloud CLI jika belum ada
# https://cloud.google.com/sdk/docs/install

# Login Application Default Credentials
gcloud auth application-default login

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

### 4. Jalankan

```bash
streamlit run app.py
```

Buka browser: `http://localhost:8501`

---

## 🏗️ Arsitektur

```
siberka-rag/
├── app.py                    # Streamlit main app
├── config.py                 # Konfigurasi terpusat
├── rag/
│   ├── document_processor.py # Parse & chunk PDF/TXT/DOCX
│   ├── embeddings.py         # Vertex AI embeddings wrapper
│   ├── vector_store.py       # ChromaDB manager
│   └── chain.py              # ConversationalRetrievalChain
├── ui/
│   ├── styles.py             # Glass morphism CSS
│   └── components.py         # Custom HTML components
├── requirements.txt
└── .env.example
```

### RAG Pipeline

```
Upload PDF/TXT/DOCX
       ↓
Document Processor (LangChain)
  • PyPDF / python-docx / plaintext
  • RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
       ↓
Vertex AI Embeddings (text-embedding-004)
  • 768-dimensional vectors
       ↓
ChromaDB (persistent local storage)
       ↓
User Query → Similarity Search (Top-5)
       ↓
ConversationalRetrievalChain
  • Condense question with chat history
  • Retrieve relevant chunks
  • Generate answer with Gemini 1.5 Flash
       ↓
Answer + Source Citations
```

---

## ⚙️ Konfigurasi Lanjutan

Edit `.env` untuk menyesuaikan parameter:

```env
# Model
GEMINI_MODEL=gemini-1.5-flash        # atau gemini-1.5-pro
EMBEDDING_MODEL=text-embedding-004

# RAG
CHUNK_SIZE=1000                       # Ukuran chunk (chars)
CHUNK_OVERLAP=200                     # Overlap antar chunk
TOP_K_RETRIEVAL=5                     # Jumlah dokumen yang diambil

# Storage
CHROMA_PERSIST_DIR=./chroma_db        # Lokasi ChromaDB
```

---

## 🔑 Prasyarat Google Cloud

1. **Project** dengan billing aktif
2. **Vertex AI API** diaktifkan:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```
3. **Permissions** yang diperlukan:
   - `roles/aiplatform.user` — untuk memanggil model
   - `roles/iam.serviceAccountUser` — opsional untuk SA

---

## 🐛 Troubleshooting

### `DefaultCredentialsError`
```bash
gcloud auth application-default login
```

### `403 Forbidden`
Pastikan Vertex AI API diaktifkan dan akun memiliki permission `aiplatform.user`.

### `GOOGLE_CLOUD_PROJECT` belum diisi
Salin `.env.example` ke `.env` dan isi project ID.

### ChromaDB error
Hapus folder `chroma_db/` dan restart aplikasi.

---

## 📦 Dependencies Utama

```
streamlit             — Web UI framework
langchain             — RAG orchestration
langchain-google-vertexai — Gemini + Vertex AI embeddings
chromadb              — Local vector database
pypdf                 — PDF parsing
python-docx           — DOCX parsing
vertexai              — Google Cloud Vertex AI SDK
```

---

## 📜 Lisensi

MIT License — bebas digunakan dan dimodifikasi.

---

<div align="center">
Built with ❤️ using Google Vertex AI · Gemini · ChromaDB · Streamlit
</div>
