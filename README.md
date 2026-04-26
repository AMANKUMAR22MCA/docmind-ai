<div align="center">

<h2>🚀 Live Demo</h2>

<a href="https://docmind-ai-1c2y.onrender.com/app/" target="_blank">
  🔗 Click here to try the app
</a>

<br/><br/>

</div>

<h3>
  <samp>🧠 Upload. Ask. Understand.</samp>
</h3>

<p>
  <em>Transform any PDF into an intelligent conversational knowledge base — powered by RAG, Groq LLM, and a blazing-fast async pipeline.</em>
</p>

<br/>

<!-- Badges -->
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python_3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq_LLM-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B35?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com/)

<br/><br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)
[![Stars](https://img.shields.io/github/stars/amanraj2418/docmind-ai?style=flat-square&color=gold)](https://github.com/amanraj2418/docmind-ai/stargazers)
[![Issues](https://img.shields.io/github/issues/amanraj2418/docmind-ai?style=flat-square&color=red)](https://github.com/amanraj2418/docmind-ai/issues)

<br/>

[**🚀 Quick Start**](#-quick-start) · [**📖 API Docs**](#-api-reference) · [**🏗 Architecture**](#-architecture) · [**🤝 Contributing**](#-contributing)

</div>

---

## 📸 Screenshots

<div align="center">

| Chat Interface | Upload & Process | API Documentation |
|:-:|:-:|:-:|
|<img width="935" height="400" alt="image" src="https://github.com/user-attachments/assets/9c2fa9fb-597d-42b1-9e64-39e5bf8c2299" />| <img width="947" height="412" alt="image" src="https://github.com/user-attachments/assets/5a09c79a-0c5a-4c20-8cb2-aee1d2f0c3e2" />
 | ![API Docs](https://via.placeholder.com/280x180/0f0f1a/34d399?text=Swagger+UI) |
| *Multi-turn dark theme chat* | *Async processing status* | *Auto-generated FastAPI docs* |

</div>

---

## ✨ Features

- 📄 **PDF Intelligence** — Upload any PDF and instantly build a searchable knowledge base
- 🤖 **RAG Pipeline** — Retrieval-Augmented Generation for accurate, context-grounded answers
- ⚡ **Async Processing** — FastAPI BackgroundTasks handles PDF ingestion non-blocking
- 🧵 **Multi-Turn Conversations** — Maintains conversation history for contextual follow-up questions
- 🗃️ **Multi-PDF Isolation** — Each document lives in its own ChromaDB namespace — no cross-contamination
- ⚡ **Redis Caching** — Blazing fast repeated query responses with intelligent cache invalidation
- 📇 **Contact Extraction** — Automatically extracts names, emails, and phone numbers from documents
- 🛡️ **Rate Limiting** — Built-in API rate limiting to prevent abuse
- 🌗 **Dark Theme UI** — Sleek HTML/JS chat interface built for power users
- 📊 **Task Monitoring** — Real-time background task status tracking via REST endpoint

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DocMind AI System                        │
│                                                                 │
│   ┌──────────────┐     ┌─────────────────────────────────────┐  │
│   │   Browser    │     │           FastAPI Backend           │  │
│   │  Dark Theme  │────▶│                                     │  │
│   │  Chat UI     │◀────│  POST /upload   POST /ask           │  │
│   └──────────────┘     │  GET  /status   GET  /docs          │  │
│                        └────────┬──────────────┬────────────┘  │
│                                 │              │               │
│              ┌──────────────────▼──┐    ┌──────▼────────────┐  │
│              │  Background Task    │    │    Redis Cache    │  │
│              │  (FastAPI built-in) │    │                   │  │
│              │  1. Parse PDF       │    │  • Query cache    │  │
│              │  2. Chunk text      │    │  • 1hr TTL        │  │
│              │  3. Embed chunks    │    │  • Per-PDF keys   │  │
│              │  4. Store vectors   │    └───────────────────┘  │
│              └──────────┬──────────┘                           │
│                         │                                      │
│              ┌──────────▼──────────┐    ┌───────────────────┐  │
│              │     ChromaDB        │    │     Groq LLM      │  │
│              │  Vector Store       │───▶│   (Inference)     │  │
│              │                     │    │                   │  │
│              │  • Per-PDF metadata │    │  • llama-3.3-70b  │  │
│              │  • Semantic search  │    │  • Ultra-low      │  │
│              │  • Top-K retrieval  │    │    latency        │  │
│              └─────────────────────┘    └───────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 RAG Pipeline — How It Works

```
 PDF Upload                 Ingestion                    Query Time
─────────────          ─────────────────────          ──────────────────────

 ┌─────────┐            ┌──────────────────┐            ┌──────────────────┐
 │  PDF    │──chunk──▶  │  Text Chunks     │  embed ──▶ │  Vector Search   │
 │  File   │            │  (900 chars)     │            │  Top-K Results   │
 └─────────┘            └──────────────────┘            └────────┬─────────┘
                                                                 │
                        ┌──────────────────┐                     │ context
                        │   ChromaDB       │◀────────────────────┘
                        │   Vector Store   │
                        └──────────────────┘      ┌──────────────────────┐
                                                   │  Prompt Assembly     │
  User Question ──────────────────────────────────▶│                      │
                                                   │  System + History +  │
                                                   │  Context + Question  │
                                                   └──────────┬───────────┘
                                                              │
                                                   ┌──────────▼───────────┐
                                                   │     Groq LLM         │
                                                   │   Generates Answer   │
                                                   └──────────────────────┘
```

> **In plain English:** Your PDF is sliced into overlapping chunks → each chunk is converted to a vector embedding → stored in ChromaDB. When you ask a question, it's also embedded → semantically similar chunks are retrieved → fed to the LLM as context → you get a precise, grounded answer. No hallucinations from thin air.

---

## 🚀 Quick Start

### Prerequisites

- 🐳 Docker & Docker Compose
- 🔑 [Groq API Key](https://console.groq.com) (free tier available)
- 🐍 Python 3.11+

### 🛠 Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/amanraj2418/docmind-ai.git
cd docmind-ai

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and REDIS_URL

# 5. Start Redis via Docker
docker-compose up -d

# 6. Launch FastAPI server
uvicorn app.main:app --reload

# 🌐 Chat UI  → http://localhost:8000/app
# 📚 API Docs → http://localhost:8000/docs
```

---

## 📡 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a PDF for async background processing |
| `POST` | `/ask` | Ask a question about a document |
| `GET` | `/status/{task_id}` | Poll background task processing status |
| `POST` | `/cache/clear` | Flush Redis response cache |
| `GET` | `/docs` | Interactive Swagger UI |

### 📤 `POST /upload`

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

```json
{
  "pdf_id": "d81e3232-e815-4b56-a497-8b7bb3bbe889",
  "task_id": "3f2e1d0c-b9a8-7654-3210-fedcba987654",
  "status": "processing"
}
```

### 💬 `POST /ask`

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What companies did Aman work at?",
    "pdf_id": "d81e3232-e815-4b56-a497-8b7bb3bbe889",
    "history": [
      {"role": "user", "content": "Summarize this resume"},
      {"role": "assistant", "content": "This is a backend engineer resume..."}
    ]
  }'
```

> You can also find a PDF by contact info instead of `pdf_id`:

```json
{
  "question": "What is his total experience?",
  "email": "amanraj241800@gmail.com",
  "history": []
}
```

```json
{
  "answer": "Aman has approximately 2 years of experience across Osfin.ai, Synoriq, Avishaan, and Kavion.ai.",
  "pdf_id": "d81e3232-e815-4b56-a497-8b7bb3bbe889"
}
```

### 🔍 `GET /status/{task_id}`

```json
{
  "task_id": "3f2e1d0c-b9a8-7654-3210-fedcba987654",
  "status": "SUCCESS",
  "result": {
    "pdf_id": "d81e3232-e815-4b56-a497-8b7bb3bbe889"
  }
}
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
# ─── LLM Configuration ────────────────────────────────────────────
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ─── Redis Configuration ──────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0

# ─── App Configuration ────────────────────────────────────────────
MAX_UPLOAD_SIZE_MB=10
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Your Groq Cloud API key |
| `REDIS_URL` | ✅ Yes | Redis connection string (supports Upstash TLS) |
| `MAX_UPLOAD_SIZE_MB` | No | Maximum PDF upload size (default: 10MB) |

---

## 📁 Project Structure

```
docmind-ai/
│
├── 📂 app/
│   ├── 📄 __init__.py
│   ├── 📄 main.py          # FastAPI app, all route definitions
│   ├── 📄 rag.py           # RAG pipeline — ingest, retrieve, answer
│   ├── 📄 schemas.py       # Pydantic request/response models
│   ├── 📄 celery_app.py    # Celery config (local dev)
│   └── 📄 tasks.py         # Celery tasks (local dev)
│
├── 📂 frontend/
│   └── 📄 index.html       # Dark theme chat interface (vanilla JS)
│
├── 📂 uploads/             # Uploaded PDFs (auto-created)
├── 📂 chroma_db/           # Vector store persistence (auto-created)
│
├── 📄 docker-compose.yml   # Redis container
├── 📄 requirements.txt
├── 📄 .env
└── 📄 README.md
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance async REST API |
| **LLM Orchestration** | [LangChain](https://langchain.com/) | RAG chain, text splitters, document loaders |
| **LLM Inference** | [Groq](https://groq.com/) | Ultra-fast LLM inference (LPU hardware) |
| **Vector Database** | [ChromaDB](https://www.trychroma.com/) | Local vector store with metadata filtering |
| **Cache** | [Redis](https://redis.io/) | Response cache with TTL (Upstash in prod) |
| **Async Tasks** | FastAPI BackgroundTasks | Non-blocking PDF ingestion |
| **PDF Parsing** | LangChain PyPDFLoader | Text extraction from PDFs |
| **Containerization** | [Docker](https://docker.com/) | Redis container via Docker Compose |
| **Frontend** | Vanilla HTML/JS | Zero-dependency dark theme chat UI |

---

## 🔬 How RAG Works (Simple Explanation)

> Think of RAG as giving the AI a textbook to look things up in — rather than relying only on what it memorized during training.

**Step 1 — 📄 Ingest**
Your PDF is parsed and split into overlapping text chunks (900 chars each). Each chunk is converted into a *vector embedding* — a list of numbers that captures semantic meaning. Contact info (name, email, phone) is automatically extracted and stored as metadata.

**Step 2 — 🗄️ Store**
All embeddings are stored in ChromaDB, tagged with your document's unique ID. This is your searchable knowledge base.

**Step 3 — 🔍 Retrieve**
When you ask a question, it's also embedded. ChromaDB finds the top-7 chunks with the most similar embeddings — filtered strictly to your document only.

**Step 4 — 🤖 Generate**
The retrieved chunks + your conversation history + your question are assembled into a structured prompt. Groq's LLM generates a precise, grounded answer. Answers are cached in Redis for 1 hour.

**Why this matters:** The AI only answers based on *your document's actual content*. If the answer isn't in the PDF, it tells you so.

---

## 🗺 Roadmap

- [ ] 🔐 JWT authentication & per-user document isolation
- [ ] ☁️ AWS S3 integration for persistent PDF storage
- [ ] 🌐 Cloud ChromaDB / Pinecone for vector persistence
- [ ] 📊 Document comparison mode (ask across multiple PDFs)
- [ ] 🌍 Multi-language document support
- [ ] 📈 Analytics dashboard (query volume, cache hit rate)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

```bash
# Fork the repo, then:
git checkout -b feature/your-amazing-feature
git commit -m "feat: add your amazing feature"
git push origin feature/your-amazing-feature
# Open a Pull Request 🎉
```

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for full details.

---

<div align="center">

### Built with ❤️ by [Aman Kumar](https://github.com/amanraj2418)

<a href="https://github.com/amanraj2418">
  <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" />
</a>
<a href="https://linkedin.com/in/aman-kumar-raj">
  <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
</a>
<a href="mailto:amanraj241800@gmail.com">
  <img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" />
</a>

<br/><br/>

*If DocMind AI saved you time, consider giving it a ⭐ — it helps a lot!*

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:24243e,50:302b63,100:0f0c29&height=120&section=footer"/>

</div>
