# rag_ingest_recursive.py — Beginner's Code Guide

> Reads all your code and document files, converts them into
> numerical vectors, and stores them in ChromaDB — a local
> vector database. This is the "feeding" step before querying.

---

## What this script does

```
Your documents folder
        ↓
Script walks every subfolder recursively
        ↓
For each supported file (.c .h .py .md etc.)
        ↓
Read the file text
        ↓
Split into chunks (512 tokens each)
        ↓
Convert each chunk to a vector (embedding) using nomic-embed-text
        ↓
Store chunk + vector + metadata in ChromaDB
        ↓
Done — ready for rag_query4.py to search
```

---

## What is a vector / embedding?

A vector is a list of numbers that represents the **meaning** of a piece of text.

```
"how to read SPI register"  →  [0.23, -0.41, 0.87, 0.12, ...]  (384 numbers)
"SPI data transfer method"  →  [0.25, -0.39, 0.85, 0.10, ...]  (similar!)
"recipe for chocolate cake" →  [-0.81, 0.33, -0.22, 0.91, ...]  (very different)
```

Two pieces of text with similar meaning will have similar vectors.
ChromaDB uses this to find relevant chunks when you ask a question.

---

## What is chunking?

Large files are split into smaller pieces before storing.

```
big_file.c (5000 characters)
        ↓
chunk 1: lines 1-40     (512 tokens)
chunk 2: lines 35-75    (512 tokens, 64 token overlap with chunk 1)
chunk 3: lines 70-110   (512 tokens)
...
```

Overlap (`chunk_overlap = 64`) ensures context is not lost at boundaries.
Smaller chunks = more precise search results.

---

## The imports

```python
import os           # os.walk() — recursively list all files and folders
import sys          # sys.argv — read command-line arguments
from pathlib import Path   # Path() — cleaner file path handling (not heavily used here)

from llama_index.core import VectorStoreIndex, Document, Settings
# VectorStoreIndex — the main index that stores and retrieves chunks
# Document         — wraps a piece of text with its metadata
# Settings         — global config for chunk size, LLM, embeddings

from llama_index.llms.ollama import Ollama
# Connection to the Ollama LLM (needed by LlamaIndex even for ingestion)

from llama_index.embeddings.ollama import OllamaEmbedding
# The embedding model — converts text chunks to vectors
# Uses nomic-embed-text running in Ollama

from llama_index.vector_stores.chroma import ChromaVectorStore
# LlamaIndex adapter that lets it talk to ChromaDB

from llama_index.core import StorageContext
# Tells LlamaIndex where to store data (in this case: ChromaDB)

import chromadb
# The vector database itself — stores chunks and their vectors on disk
```

---

## Configuration

```python
OLLAMA_URL = "http://10.0.0.38:11434"
```
Where Ollama is running. Both the LLM and the embedding model live here.

```python
LLM_MODEL  = "qwen2.5-coder:7b"
EMBED_MODEL = "nomic-embed-text"
```
- `LLM_MODEL` — used by LlamaIndex internally (required even for ingest)
- `EMBED_MODEL` — this is the important one for ingestion. It converts
  your text chunks into vectors. `nomic-embed-text` is a small, fast,
  high-quality embedding model.

```python
CHROMA_PATH     = "./chroma_db"
COLLECTION_NAME = "code_files"
```
- `CHROMA_PATH` — folder where ChromaDB saves its files on disk.
  Created automatically. Contains binary index files — don't edit manually.
- `COLLECTION_NAME` — like a table name in a regular database.
  All chunks go into this collection. Must match what rag_query4.py uses.

```python
SUPPORTED_TYPES = (
    ".c", ".h", ".cpp", ".ino",
    ".md", ".txt",
    ".py", ".js", ".java",
    ".xml", ".json",
)
```
Only files with these extensions are processed. Everything else is ignored.
Add extensions here if you need to ingest other file types.

```python
SKIP_FOLDERS = {
    '.git', '__pycache__', 'node_modules',
    '.venv', 'venv', '.DS_Store'
}
```
Folders to skip during the recursive walk. These contain either
version control data, compiled cache, or system files — not useful to ingest.

---

## LLM and embedding setup

```python
Settings.llm = Ollama(
    model=LLM_MODEL,
    base_url=OLLAMA_URL,
    request_timeout=600
)
```
LlamaIndex requires an LLM to be configured even for ingestion.
It's used internally for some metadata operations.

```python
Settings.embed_model = OllamaEmbedding(
    model_name=EMBED_MODEL,
    base_url=OLLAMA_URL
)
```
The embedding model is what does the real work during ingestion.
Every chunk of text is sent to `nomic-embed-text` which returns
a vector (list of 384 numbers) representing its meaning.

```python
Settings.chunk_size    = 512    # max tokens per chunk
Settings.chunk_overlap = 64     # tokens shared between adjacent chunks
```
These are global settings that apply to every document processed.
`chunk_overlap` ensures that sentences at chunk boundaries are
included in both chunks — so context is not lost.

---

## ChromaDB setup

```python
chroma_client     = chromadb.PersistentClient(path=CHROMA_PATH)
```
Opens (or creates) a ChromaDB database stored at `./chroma_db`.
`PersistentClient` means data is saved to disk — not lost when the script ends.

```python
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
```
Gets the collection named `"code_files"` if it exists,
or creates it if it doesn't. Safe to run multiple times — won't duplicate the collection.

```python
vector_store    = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
```
Wraps the ChromaDB collection in LlamaIndex's interface so
`VectorStoreIndex` knows where to save chunks and vectors.

---

## find_all_files()

```python
def find_all_files(directory, supported_types, skip_folders):
```

Uses `os.walk()` which recursively visits every subfolder:

```
os.walk("./my_project/") yields:
  ("./my_project/",        ["src", "docs"],       ["README.md"])
  ("./my_project/src/",    ["drivers"],            ["main.c", "main.h"])
  ("./my_project/src/drivers/", [],               ["spi.c", "spi.h"])
  ("./my_project/docs/",   [],                    ["datasheet.pdf"])
```

Each iteration gives: `(current_folder, [subfolders], [files_in_folder])`

```python
dirs[:] = [d for d in dirs if d not in skip_folders]
```
`dirs[:]` modifies the list IN PLACE. This is important — `os.walk` reads
`dirs` to decide which subfolders to visit next. By modifying it here
we prevent `os.walk` from ever entering the skipped folders.
This is faster than skipping files after the fact.

```python
file_ext = os.path.splitext(filename)[1].lower()
```
`os.path.splitext("spi_driver.c")` returns `("spi_driver", ".c")`.
`[1]` gets the extension. `.lower()` handles `.C` and `.c` the same way.

---

## ingest_file()

```python
def ingest_file(file_path):
```

### Step 1 — Read the file

```python
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()
```
`errors="ignore"` skips any characters that can't be decoded as UTF-8.
This handles binary-ish files and mixed encodings without crashing.

```python
if not text.strip():
    return False
```
Skip empty files — nothing to ingest.

### Step 2 — Create a Document

```python
document = Document(
    text=text,
    metadata={
        "filename": file_name,
        "source":   file_path,
        "rel_path": rel_path,
        "type":     "code" if file_ext in [...] else "text",
        "file_size": file_size,
        "file_ext":  file_ext,
    }
)
```

`Document` is a LlamaIndex wrapper that holds:
- `text` — the actual file content
- `metadata` — information about the file stored alongside each chunk

Metadata is returned with search results in rag_query4.py, so you know
**which file** each answer came from. Think of it as a label on each chunk.

### Step 3 — Store in ChromaDB

```python
VectorStoreIndex.from_documents(
    [document],
    storage_context=storage_context,
    show_progress=False
)
```

LlamaIndex does several things here automatically:
1. Splits the document into chunks (using `chunk_size` and `chunk_overlap`)
2. Sends each chunk to `nomic-embed-text` → gets back a vector
3. Stores (chunk text + vector + metadata) in ChromaDB

This is the slowest step — each chunk requires a call to the embedding model.

---

## main()

```python
target = os.path.expanduser(target)
```
Expands `~` to the home directory:
`~/arduino15/` → `/Users/alex/arduino15/`

```python
files = find_all_files(target, SUPPORTED_TYPES, SKIP_FOLDERS)
```
Gets the complete list of files to process before starting.
This way we can show progress `[3/47]`.

```python
for i, file_path in enumerate(files, 1):
    print(f"[{i}/{len(files)}]")
    if ingest_file(file_path):
        successful += 1
    else:
        failed += 1
```
`enumerate(files, 1)` — gives `(1, file1), (2, file2), ...`
(starting from 1 instead of 0 for human-readable display).

### Final summary

```python
total_chunks = chroma_collection.count()
print(f"   Total chunks:  {total_chunks}")
```
`chroma_collection.count()` returns the total number of chunks
stored in ChromaDB — including any from previous ingest runs.
One file typically produces 5-50 chunks depending on its size.

---

## What gets stored in ChromaDB

For each file chunk ChromaDB stores:

```
┌─────────────────────────────────────────────┐
│ ID:       unique identifier                 │
│ Vector:   [0.23, -0.41, 0.87, ...]          │  ← 384 numbers
│ Text:     "void spi_init() {\n  ..."        │  ← the actual code
│ Metadata: {                                  │
│   filename: "spi_driver.c",                 │
│   rel_path: "src/drivers/spi_driver.c",     │
│   file_ext: ".c",                           │
│   type:     "code"                          │
│ }                                            │
└─────────────────────────────────────────────┘
```

When you query with rag_query4.py:
1. Your question is converted to a vector by `nomic-embed-text`
2. ChromaDB finds the TOP_K chunks whose vectors are most similar
3. Those chunks are sent to the LLM as context

---

## How to run

```bash
# ingest all files in a folder (recursive)
python3 rag_ingest_recursive.py ./my_documents/

# ingest Arduino libraries
python3 rag_ingest_recursive.py ~/.arduino15/packages/esp32/

# check how many chunks are stored
python3 -c "
import chromadb
c = chromadb.PersistentClient('./chroma_db')
print(c.get_or_create_collection('code_files').count(), 'chunks')
"

# clear the database and start fresh
rm -rf chroma_db/
python3 rag_ingest_recursive.py ./my_documents/
```

---

## Summary — data flow

```
python3 rag_ingest_recursive.py ./documents/
        ↓
find_all_files() — walks all subfolders
        ↓
for each file:
  read text
  create Document with metadata
        ↓
  VectorStoreIndex.from_documents()
        ↓
  split into 512-token chunks
        ↓
  each chunk → nomic-embed-text → vector [384 numbers]
        ↓
  store (text + vector + metadata) in chroma_db/
        ↓
done — chroma_db/ ready for rag_query4.py
```

---

*Guide written April 2026*
