# Installation & Setup Guide
## chat.py · rag_query4.py · rag_query_3.py
### macOS

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Python installation](#2-python-installation)
3. [Python packages](#3-python-packages)
4. [Ollama installation](#4-ollama-installation)
5. [Download models](#5-download-models)
6. [Enable remote Ollama access](#6-enable-remote-ollama-access)
7. [Folder structure](#7-folder-structure)
8. [Quick start](#8-quick-start)

---

## 1. Prerequisites

- macOS 12 or later
- Homebrew — install if missing:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## 2. Python installation

```bash
# install Python 3.11 (recommended — best LlamaIndex compatibility)
brew install python@3.11

# verify
python3 --version
```

> **Note:** macOS ships with Python 3 but it may be outdated. Use Homebrew's version.

---

## 3. Python packages

### Core dependencies

```bash
# LlamaIndex — RAG framework used by rag_query4.py and rag_query_3.py
pip3 install llama-index-core

# Ollama integration for LlamaIndex
pip3 install llama-index-llms-ollama
pip3 install llama-index-embeddings-ollama

# ChromaDB — vector database for storing document chunks
pip3 install chromadb
pip3 install llama-index-vector-stores-chroma

# Ollama Python client — used by chat.py
pip3 install ollama
```

### All packages in one command

```bash
pip3 install \
  llama-index-core \
  llama-index-llms-ollama \
  llama-index-embeddings-ollama \
  llama-index-vector-stores-chroma \
  chromadb \
  ollama
```

### Verify installation

```bash
python3 -c "
from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import SimpleChatEngine
import chromadb
print('All packages OK')
"
```

---

## 4. Ollama installation

### Option A — Ollama runs locally on your Mac

```bash
# install Ollama
brew install ollama

# start the Ollama service
ollama serve

# verify it is running
curl http://localhost:11434
# should return: Ollama is running
```

To run Ollama as a background service:
```bash
brew services start ollama
```

### Option B — Ollama runs on a remote Ubuntu machine

Skip this section — see [Section 6](#6-enable-remote-ollama-access) instead.

---

## 5. Download models

### Models used by these scripts

| Model | Used by | Purpose |
|-------|---------|---------|
| `qwen2.5-coder:7b` | chat.py, rag_query4.py, rag_query_3.py | main LLM for answers |
| `nomic-embed-text` | rag_query4.py, rag_query_3.py | embedding documents for RAG search |

### Pull the models

```bash
# main language model
ollama pull qwen2.5-coder:7b

# embedding model (needed for RAG only)
ollama pull nomic-embed-text

# verify both are downloaded
ollama list
```

Expected output:
```
NAME                    ID              SIZE
qwen2.5-coder:7b        xxxxxxxxxxxx    4.7 GB
nomic-embed-text        xxxxxxxxxxxx    274 MB
```

---

## 6. Enable remote Ollama access

If Ollama runs on a **remote Ubuntu machine** (e.g. your main workstation at `10.0.0.38`), you need to allow connections from other machines.

### On the Ubuntu machine running Ollama

```bash
# stop Ollama if running
sudo systemctl stop ollama

# edit the Ollama service file
sudo nano /etc/systemd/system/ollama.service
```

Find the `[Service]` section and add:
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Save and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl start ollama
sudo systemctl status ollama
```

### Verify remote access from your Mac

```bash
curl http://10.0.0.38:11434
# should return: Ollama is running

curl http://10.0.0.38:11434/api/tags
# should return list of installed models as JSON
```

### Update scripts to point to remote Ollama

In all three scripts, set:
```python
OLLAMA_URL = "http://10.0.0.38:11434"   # your Ubuntu machine IP
```

If running locally on Mac instead:
```python
OLLAMA_URL = "http://localhost:11434"
```

---

## 7. Folder structure

```
your_project/
│
├── chat.py              ← simple chatbot
├── rag_query4.py        ← RAG query with chat_engine
├── rag_query_3.py       ← RAG query with query_engine
│
├── chroma_db/           ← vector database (auto-created by ingest)
│   └── ...              ← ChromaDB internal files
│
├── documents/           ← put your source files here before ingesting
│   ├── datasheet.pdf
│   ├── source_code.c
│   └── ...
│
└── output/              ← auto-created on first run
    ├── chat_session_20260425_143207.md    ← chat.py sessions
    └── session_20260425_150312.md         ← rag_query sessions
```

### Create folders

```bash
mkdir -p documents
mkdir -p output
# chroma_db is created automatically when you run ingest
```

### Ingest documents into ChromaDB

Before using rag_query4.py or rag_query_3.py you must ingest your documents:

```bash
# run the ingest script pointing at your documents folder
python3 rag_ingest_recursive.py documents/

# verify chunks were created
python3 -c "
import chromadb
c = chromadb.PersistentClient('./chroma_db')
col = c.get_or_create_collection('code_files')
print(f'Chunks in database: {col.count()}')
"
```

---

## 8. Quick start

### chat.py — simple chatbot

```bash
python3 chat.py
```

Type your message, press Enter for new lines, type `.` alone to send.
Type `/bye` to exit. Session saved to `output/chat_session_TIMESTAMP.md`.

---

### rag_query4.py — RAG with chat engine

```bash
# interactive mode
python3 rag_query4.py

# single question mode
python3 rag_query4.py "What is the SPI init sequence?"
```

Session saved to `output/session_TIMESTAMP.md`.

---

### rag_query_3.py — RAG with query engine

```bash
# interactive mode
python3 rag_query_3.py

# single question mode
python3 rag_query_3.py "List all register addresses"
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ImportError: cannot import name 'Ollama'` | `pip3 install llama-index-llms-ollama` |
| `Connection refused` on Ollama URL | check `ollama serve` is running, check IP |
| `No data in database` | run ingest script first |
| `ModuleNotFoundError: chromadb` | `pip3 install chromadb` |
| `ollama: command not found` | `brew install ollama` |

---

*Guide written for macOS · April 2026*
