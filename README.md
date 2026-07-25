# CareerQA

RAG-powered application that intelligently answers interview questions based on career history, tailored to the target company.

## How it works

1. **Docs** — career history is written as structured Markdown files (`retrieval-augmented-generation/docs/`)
2. **Ingest** — documents are chunked and converted into embeddings (vectors) locally, then stored in a local vector database
3. **Retrieve** — a question (plus an optional target company/domain) is embedded the same way and matched against stored chunks to find the most relevant ones
4. **Prompt** — the backend assembles those chunks + the question into a final, ready-to-use prompt
5. **You paste it** — into ChatGPT, Claude, or any LLM chat you like. No API key, no per-query cost, no vendor lock-in.

## Stack

- **Python 3** — `sentence-transformers` (local embeddings) + `ChromaDB` (local vector store)
- **NestJS** (`backend/`) — receives a question, runs local retrieval, assembles the final prompt
- **Vue 3 + Vite** (`frontend/`) — form for company name / company context / question, shows the copy-ready prompt

## Structure

```
career-qa/
├── install.sh                           # one-command environment setup (run from repo root)
├── frontend/                            # Vue 3 + Vite — form + copy-ready output
├── backend/                             # NestJS — POST /prompt endpoint
└── retrieval-augmented-generation/      # Python — docs, chunking, local embeddings, local vector store
    ├── docs/                            # career history, written as Markdown
    │   ├── career-overview.md           # high-level career narrative/timeline
    │   ├── companies/                   # one file per company — role, duration, progression
    │   └── projects/                    # one file per project — deep-dive (why/how/challenges/outcome)
    ├── ingest.py                        # chunk + embed + store docs/ into a local vector DB
    ├── retrieve.py                      # retrieve the top matching chunks for a question, as JSON
    └── requirements.txt
```

## Doc template

Company files (`docs/companies/*.md`) and project files (`docs/projects/*.md`) use YAML frontmatter for metadata, plus consistent section headers so retrieval returns coherent, self-contained chunks. Project files follow:

```markdown
---
company:
role:
duration:
project:
---

# <Project Name>

## Context
## Why
## How
## Challenges
## Outcome & Impact
```

## Getting started

**Python retrieval engine** (working today):

```bash
chmod +x install.sh   # grants execute permission — one-time only, see note below
./install.sh
cd retrieval-augmented-generation && source venv/bin/activate
python ingest.py                                    # builds the local vector store from docs/
python retrieve.py "your question" --company "optional target company"
```

> `chmod +x install.sh` grants the script permission to be run directly (`./install.sh`) — without it you'd get a `Permission denied` error. This is a one-time step per clone; the permission is saved as a property of the file itself, so you never need to run it again after the first time.

`retrieve.py` prints a single JSON object containing the top matching chunks, so it can be consumed by another process — the NestJS backend does this next.

**Backend / frontend** — not built yet; see Status below.

## Status

- [x] Repo scaffolded
- [x] Docs folder structure + templates defined
- [x] `ingest.py` — chunk, embed, store docs
- [x] `retrieve.py` — retrieval-only, JSON output (verified working)
- [ ] Real career content fully fleshed out (drafted from resume/cover letter; narrative sections still need manual detail — see `<!-- TODO -->` markers)
- [ ] NestJS backend (`POST /prompt`)
- [ ] Vue frontend (form + copy-ready output)
- [ ] End-to-end test
