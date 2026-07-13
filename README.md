# RAG CV Chatbot

A Retrieval-Augmented Generation chatbot that answers recruiter questions about a professional profile (CV, projects, certifications, academic background) grounded strictly in curated source documents. The system is split into three independently deployable services: a content ingestion pipeline, a retrieval/generation API, and a web chat client.

## Table of Contents

- [Goal](#goal)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [How It Works](#how-it-works)
  - [Ingestion Pipeline](#ingestion-pipeline)
  - [Retrieval](#retrieval)
  - [Generation](#generation)
- [Data Model](#data-model)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Database](#1-database)
  - [2. Ingestion Service](#2-ingestion-service)
  - [3. Retrieval API](#3-retrieval-api)
  - [4. Web Client](#4-web-client)
- [Environment Variables](#environment-variables)
- [Common Commands](#common-commands)
- [Design Decisions](#design-decisions)
- [Known Limitations and Future Work](#known-limitations-and-future-work)
- [License](#license)

## Goal

Recruiters and hiring managers rarely read a full CV end to end, and a static PDF cannot answer follow-up questions. This project turns a professional profile into a conversational interface: a recruiter can ask open questions ("What experience does he have with Kubernetes?", "Tell me about the appPartidito project") and get answers sourced directly from the CV, an "about me" document, certifications, academic history, and the READMEs of real GitHub projects — with the system explicitly refusing to answer from outside that corpus.

The project intentionally favors a small, transparent, self-hosted pipeline (own Postgres + pgvector, open embedding model, a single LLM call) over a managed vector-database/agent framework, since the corpus is small and the goal is full control over what gets retrieved and why.

## Architecture

```
                         ┌────────────────────────┐
                         │   sources/ (markdown,   │
                         │   csv, GitHub READMEs)  │
                         └───────────┬────────────┘
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │       ingestion         │
                         │  (batch / CronJob-style)│
                         │  load -> chunk -> embed  │
                         └───────────┬────────────┘
                                     │ writes
                                     ▼
                         ┌────────────────────────┐
                         │   PostgreSQL + pgvector  │
                         │   "chunks" / "messages"  │
                         └───────────┬────────────┘
                                     │ reads
                                     ▼
┌──────────────┐        ┌────────────────────────┐        ┌───────────────┐
│  rag-client   │  HTTP  │      retrieval-api       │  HTTP  │   Groq API     │
│  (React SPA)  │◄──────►│  embed query -> vector    │◄──────►│  (LLM inference)│
│               │  /chat │  search -> diversify ->   │        │                │
│               │        │  build prompt -> generate │        │                │
└──────────────┘        └────────────────────────┘        └───────────────┘
```

The three services do not share code or a network boundary at runtime beyond the database and their public HTTP APIs. They are deployed and versioned independently:

- **`ingestion/`** — an offline batch job. Reads the source documents, chunks them, embeds each chunk, and fully re-syncs the `chunks` table in Postgres. Meant to run as a one-off job or a scheduled Kubernetes CronJob, not as a long-running service.
- **`retrieval-api/`** — a FastAPI service that embeds incoming questions, runs a similarity search against the same Postgres table, builds a grounded prompt, and calls Groq's hosted LLM to generate the answer. Also owns conversation history.
- **`rag-client/`** — a Vite + React + TypeScript single-page app that provides the chat UI and talks to `retrieval-api` over HTTP.

## Repository Structure

```
.
├── ingestion/                  Batch ingestion pipeline
│   ├── core/                   Settings, DB engine, SQLAlchemy Chunk model
│   ├── sources/                Source-of-truth content (see sources/README.md)
│   │   ├── cv/                 CV markdown
│   │   ├── about_me/           "About me" Q&A-style markdown
│   │   ├── certificados/       One markdown per certification
│   │   ├── plan_estudio/       Academic history (CSV + narrative summary)
│   │   └── readmes/            Manually written READMEs + repos_links.md
│   ├── frontmatter.py          Minimal YAML-like frontmatter parser
│   ├── heading_splitter.py     Markdown heading-based text splitter
│   ├── chunkers.py             Per-source-type chunking strategies
│   ├── loaders.py              Reads sources/ and produces IngestChunk lists
│   ├── github_client.py        Live README fetch via the GitHub API
│   ├── run.py                  Entry point: load -> embed -> full re-sync into Postgres
│   └── Dockerfile
├── retrieval-api/               Retrieval + generation service (FastAPI)
│   └── app/
│       ├── core/                Settings, DB engine, ORM models (Chunk, ChatMessage)
│       ├── routers/chat.py      POST /chat endpoint
│       ├── services/
│       │   ├── retrieval.py     Embedding + vector search + source diversification
│       │   ├── generation.py    Prompt construction + Groq call
│       │   ├── history.py       Conversation history persistence
│       │   └── schemas.py       Pydantic response/internal models
│       └── main.py               App factory, lifespan (loads embedding model), CORS
│   └── Dockerfile
└── rag-client/                  Chat UI (Vite + React + TypeScript + Tailwind)
    └── src/
        ├── components/           ChatInput, MessageList, TypewriterHeading, Footer
        ├── hooks/                useConversation, useChatInput, useTypewriter
        └── types/                Shared TypeScript types
```

## How It Works

### Ingestion Pipeline

`ingestion/run.py` is the single entry point (`python run.py`):

1. **Load** — `loaders.py` walks `sources/` by subfolder, one loader function per content type (`load_cv`, `load_about_me`, `load_certificados`, `load_plan_estudio`, `load_proyectos`). Markdown files may carry a simple frontmatter block (`nombre`, `fuente_url`); a missing or `null` value is treated as absent.
2. **Fetch project READMEs** — `load_proyectos` combines two sources of project documentation:
   - `sources/readmes/repos_links.md` lists public GitHub repositories (one URL per line) whose READMEs are **fetched live** from the GitHub API (`github_client.py`) at ingestion time, so they always reflect the current state of those repos.
   - Any other `.md` file in `sources/readmes/` is a README written by hand in this repository, for private repositories or ones without a README worth showing as-is. The project title comes from the first `# heading`, and the canonical GitHub link from a `**Repositorio:** <url>` line if present.
3. **Chunk** — `chunkers.py` picks a strategy per content type:
   - CV, about-me, plan-estudio summary, and long READMEs are split by Markdown heading (`heading_splitter.py`), so each heading becomes one self-contained, topically coherent chunk. A heading with no body text is merged into the following block instead of producing an empty chunk.
   - Short READMEs (below `SHORT_README_THRESHOLD`, 800 characters) are kept as a single chunk — splitting a short document adds fragmentation without adding retrievability.
   - Certifications are never split (they are already short and self-contained).
   - Academic history rows (`plan_estudio/*.csv`) become one chunk per course, so pointed questions ("which AI courses did he pass?") can be answered precisely instead of via a bulky narrative summary.
4. **Embed** — every chunk's `content` is embedded with `Qwen/Qwen3-Embedding-0.6B` via `sentence-transformers`.
5. **Persist** — the entire `chunks` table is deleted and re-inserted inside a single transaction (full re-sync, not an upsert/diff).

### Retrieval

`retrieval-api/app/services/retrieval.py` handles `retrieve_context`:

1. The user's question is embedded with the same model used during ingestion (this is load-bearing — a mismatched model puts queries and chunks in different vector spaces).
2. A cosine-distance nearest-neighbor search (`pgvector`) pulls a **candidate pool** (30 chunks) rather than only the final `top_k`.
3. Candidates with distance above `0.7` are dropped — this is a coarse guardrail against answering questions clearly outside the corpus, not a precision tool.
4. The candidate pool is **diversified by source** (`nombre`): at most one chunk per source is taken first, in distance order, and only once every source has had a chance does the selection fall back to a source's remaining chunks. This exists because a single dense, keyword-rich chunk — typically the CV — tends to score well against almost any technical question and would otherwise occupy most or all of the final slots, crowding out project READMEs that are just as relevant. Widening the pool and diversifying by source before truncating to `top_k` (6) fixes that without touching the chunking or embedding model.

### Generation

`retrieval-api/app/services/generation.py`:

1. Builds a system prompt that restricts the model to the retrieved context, instructs it to say so explicitly when the context is insufficient, and to attribute claims to their source.
2. Formats each retrieved chunk as `[Fuente: <name> — <source URL if any>]` followed by its content, so the model can cite a real GitHub link when one exists.
3. Sends system prompt + recent conversation history + the current question and context to Groq (`llama-3.3-70b-versatile`) and returns the completion. A `RateLimitError` is caught and turned into a user-facing "try again later" message instead of a hard failure.

Conversation history (`services/history.py`) is persisted per `conversation_id` in the `messages` table and the last 10 turns are replayed on each request; the client keeps the `conversation_id` in `sessionStorage` so a page refresh continues the same conversation.

## Data Model

Two tables, defined independently in `ingestion/core/models.py` and `retrieval-api/app/core/models.py` (see [Design Decisions](#design-decisions) for why):

**`chunks`**

| Column      | Type          | Notes                                                        |
|-------------|---------------|---------------------------------------------------------------|
| id          | int, PK       |                                                                 |
| content     | text          | The chunk text sent to the embedding model and to the LLM      |
| embedding   | vector(1024)  | Must match the embedding model's output dimension              |
| tipo        | string        | `cv` \| `about_me` \| `certificado` \| `plan_estudio` \| `proyecto` |
| nombre      | string        | Human-readable source name, used for diversification and citation |
| fuente_url  | string, null  | Canonical URL (e.g. GitHub repo) when one exists                |

**`messages`**

| Column          | Type      | Notes                              |
|-----------------|-----------|-------------------------------------|
| id              | int, PK   |                                      |
| conversation_id | string    | Indexed, groups turns of one chat    |
| role            | string    | `user` \| `assistant`               |
| content         | text      |                                      |
| created_at      | timestamp | Server-side default                 |

## Tech Stack

| Layer            | Choice                                              |
|-------------------|------------------------------------------------------|
| Embeddings        | `Qwen/Qwen3-Embedding-0.6B` via `sentence-transformers` |
| Vector store      | PostgreSQL + `pgvector`                              |
| LLM inference     | Groq API, `llama-3.3-70b-versatile`                  |
| Backend framework | FastAPI, SQLAlchemy (async), asyncpg                 |
| Ingestion         | Plain Python script, no orchestration framework      |
| Frontend          | React 19, TypeScript, Vite, Tailwind CSS, axios      |
| Containerization  | Docker (one `Dockerfile` per backend service)        |

## Getting Started

### Prerequisites

- Python 3.12
- Node.js 20+
- PostgreSQL with the `pgvector` extension available (`CREATE EXTENSION vector;`)
- A Groq API key (for `retrieval-api`)
- Optionally, a GitHub personal access token (for `ingestion`, to raise the API rate limit when fetching READMEs live)

### 1. Database

Create a database and enable `pgvector` once:

```bash
psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE retrieval;"
psql -h localhost -p 5433 -U postgres -d retrieval -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Both `ingestion` and `retrieval-api` create their tables automatically on startup (`Base.metadata.create_all`), so no separate migration step is required.

### 2. Ingestion Service

```bash
cd ingestion
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL, EMBEDDING_MODEL_NAME, GITHUB_TOKEN
python run.py
```

This populates the `chunks` table from `sources/`. Re-run it any time source content changes — it fully replaces the table's contents in one transaction.

### 3. Retrieval API

```bash
cd retrieval-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GROQ_API_KEY, DATABASE_URL, EMBEDDING_MODEL_NAME
uvicorn app.main:app --reload --port 8000
```

`EMBEDDING_MODEL_NAME` must be identical to the value used by `ingestion`, otherwise queries and stored chunks live in different vector spaces and similarity search becomes meaningless.

### 4. Web Client

```bash
cd rag-client
npm install
npm run dev
```

The client currently points at `http://localhost:8000/chat` (hardcoded in `src/hooks/useConversation.ts`); update that constant before deploying against a non-local API. The dev server runs on Vite's default port (5173), which is also the only origin allowed by `retrieval-api`'s CORS configuration.

## Environment Variables

**`ingestion/.env`**

| Variable             | Required | Description                                                        |
|----------------------|----------|----------------------------------------------------------------------|
| `DATABASE_URL`        | yes      | `postgresql+asyncpg://user:password@host:port/db`                    |
| `EMBEDDING_MODEL_NAME`| yes      | Must match `retrieval-api`'s value                                    |
| `GITHUB_TOKEN`        | no       | Raises the GitHub API rate limit when fetching READMEs live           |

**`retrieval-api/.env`**

| Variable             | Required | Description                                       |
|----------------------|----------|-----------------------------------------------------|
| `GROQ_API_KEY`        | yes      | Groq API key used for chat completions              |
| `DATABASE_URL`        | yes      | Same database as `ingestion`                        |
| `EMBEDDING_MODEL_NAME`| yes      | Must match `ingestion`'s value                       |

## Common Commands

| Task                              | Command                                                |
|-------------------------------------|-----------------------------------------------------------|
| Re-ingest all sources                | `cd ingestion && python run.py`                            |
| Run the API locally                  | `cd retrieval-api && uvicorn app.main:app --reload --port 8000` |
| Run the client locally               | `cd rag-client && npm run dev`                             |
| Lint the client                      | `cd rag-client && npm run lint`                             |
| Build the client for production      | `cd rag-client && npm run build`                            |
| Build the ingestion image            | `docker build -t rag-ingestion ./ingestion`                 |
| Build the API image                  | `docker build -t rag-retrieval-api ./retrieval-api`         |
| Run the API container                | `docker run --env-file retrieval-api/.env -p 8000:8000 rag-retrieval-api` |

## Design Decisions

- **Full re-sync ingestion instead of upsert/diff.** The corpus is small (a few hundred chunks), so deleting and re-inserting the whole `chunks` table inside one transaction on every run is simpler and more reliable than tracking per-document diffs, at negligible cost.
- **Heading-based chunking, not fixed-size windows.** CV, about-me, and long READMEs are structured documents where a Markdown heading already marks a topical boundary. Splitting there keeps each chunk self-contained and avoids the arbitrary mid-sentence cuts of fixed-size or sliding-window chunking.
- **Short documents are not split.** Below an 800-character threshold, forcing a document into several sub-chunks only fragments context without adding retrievability, so it is kept whole.
- **Two sources for project documentation.** Public repositories with a good README are fetched live from GitHub at ingestion time, so that content never goes stale relative to the actual repo. Private repositories, or ones whose README does not stand on its own, get a hand-written README committed to `sources/readmes/`, with the real repository link preserved for citation.
- **Source-diversified retrieval.** A naive top-k nearest-neighbor search let one dense, keyword-heavy chunk (in practice, the consolidated CV) dominate the result set for almost any technical question, crowding out equally relevant project READMEs. Pulling a wider candidate pool and capping it to one chunk per source before backfilling remaining slots fixes this without touching the embedding model or the chunking strategy.
- **A coarse distance cutoff (0.7), not a precision filter.** Its purpose is only to stop the model from confidently answering questions that have no business being answered from this corpus at all; the system prompt is the primary mechanism for keeping answers grounded.
- **Same embedding model in both services, configured independently.** `ingestion` and `retrieval-api` do not share a settings module, so `EMBEDDING_MODEL_NAME` must be kept in sync by hand between their two `.env` files. This is a deliberate simplicity/coupling trade-off: the two services are meant to be deployed and scaled independently, at the cost of a manual invariant to maintain.
- **Duplicated `Chunk` ORM model.** Both services define their own SQLAlchemy model for the same `chunks` table instead of sharing a package, for the same independent-deployment reason above; a schema change must be applied to both models by hand.
- **Client-side conversation continuity via `sessionStorage`.** The server is the source of truth for conversation history (`messages` table), but the client only needs to remember the `conversation_id` to keep resubmitting it; `sessionStorage` is enough for that and avoids setting up cookies or auth for a single-tenant portfolio chatbot.
- **Groq over a self-hosted LLM.** Given a small, well-scoped, low-traffic use case, a hosted low-latency LLM API is a simpler and cheaper trade-off than serving a large model.

## Known Limitations and Future Work

- The client's API base URL is hardcoded (`src/hooks/useConversation.ts`); it should be moved to a build-time environment variable before deploying against anything other than `localhost:8000`.
- CORS on `retrieval-api` currently allows only `http://localhost:5173`; a production deployment needs its real origin added.
- There is no authentication, rate limiting, or abuse protection in front of `retrieval-api` beyond Groq's own `RateLimitError` handling.
- No automated test suite exists for any of the three services yet.
- `retrieval-api/app/models/models.py` is currently unused and can be removed once confirmed dead.
- The `ingestion` Dockerfile is written to run as a one-off Job or scheduled CronJob; the actual Kubernetes manifests for that scheduling are not part of this repository.

## License

No license file is currently included in this repository. All rights reserved by the author unless a license is added.
