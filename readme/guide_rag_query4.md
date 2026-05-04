# rag_query4.py — Beginner's Code Guide

> Searches your ingested documents using ChromaDB, sends the
> relevant chunks plus your question to Ollama, and streams
> back the answer. Remembers the conversation automatically.

---

## What this script does

```
You ask a question
        ↓
Your question is converted to a vector (embedding)
        ↓
ChromaDB finds the TOP_K most relevant document chunks
        ↓
Those chunks + conversation history + your question → Ollama
        ↓
Answer is streamed token by token to the screen
        ↓
Q&A is appended to the session .md file
```

This is called **RAG — Retrieval Augmented Generation**.
Instead of the model guessing from training data,
it reads YOUR documents and answers from those.

---

## RAG vs plain chat — why it matters

```
Plain chat (chat.py):
  Q: "How do I init the ADXL362?"
  A: [model guesses from training — may be wrong or outdated]

RAG (rag_query4.py):
  Q: "How do I init the ADXL362?"
  → searches your datasheet chunks
  → finds the actual init sequence from the PDF
  A: [model answers from YOUR document — accurate]
```

---

## The imports

```python
import datetime   # for session filename timestamp
import sys        # sys.argv (command-line args), sys.exit()
import os         # os.makedirs() for output/ folder
import chromadb   # the vector database

from llama_index.core import VectorStoreIndex, Settings
# VectorStoreIndex — the search index over ChromaDB
# Settings         — global LLM and embedding configuration

from llama_index.llms.ollama import Ollama
# Connection to the Ollama LLM

from llama_index.embeddings.ollama import OllamaEmbedding
# Embedding model — converts your question to a vector for searching

from llama_index.vector_stores.chroma import ChromaVectorStore
# LlamaIndex ↔ ChromaDB bridge

from llama_index.core import StorageContext
# Tells LlamaIndex to use ChromaDB as storage backend

from llama_index.core.memory import ChatMemoryBuffer
# Manages conversation history — keeps last HISTORY_BUFFER tokens
# Drops oldest messages automatically when full
```

---

## Configuration

```python
OLLAMA_URL  = "http://10.0.0.38:11434"   # Ollama server IP
LLM_MODEL   = "qwen2.5-coder:7b"         # language model for answers
EMBED_MODEL = "nomic-embed-text"          # embedding model for search
CHROMA_PATH = "./chroma_db"              # where the vector DB lives on disk
COLLECTION  = "code_files"               # which collection to search
```

```python
TEMPERATURE = 0.2
```
Controls how creative the model is.
- `0.0` = deterministic, always the same answer (good for code/facts)
- `1.0` = very creative, more varied answers (good for writing)
- `0.2` = slightly creative, mostly consistent — good for technical Q&A

```python
NUM_PREDICT = 512
```
Maximum number of tokens in the model's response.
512 tokens ≈ ~380 words. Increase for longer answers.

```python
TOP_K = 5
```
How many document chunks to retrieve from ChromaDB per question.
5 chunks ≈ ~2000 tokens of relevant context sent to the model.
Increase for broader coverage, decrease for more focused answers.

```python
MAX_CONTEXT_WINDOW = 8192
```
The model's total token limit per call.
Everything — system prompt + history + RAG chunks + question + answer —
must fit within this number.

```python
HISTORY_BUFFER = 4500
```
Tokens reserved for conversation history.
```
8192 (total)
- 512  system prompt
- 2000 RAG chunks (5 chunks × ~400 tokens)
- 512  current question
- 512  response
─────────────────
4656  available for history  →  we use 4500 (safe margin)
```

---

## LLM setup

```python
Settings.llm = Ollama(
    model=LLM_MODEL,
    base_url=OLLAMA_URL,
    request_timeout=600,
    temperature=TEMPERATURE,
    num_predict=NUM_PREDICT,
    top_p=TOP_P,
    context_window=MAX_CONTEXT_WINDOW,
    system_prompt=SYSTEM_PROMPT,
)
```

`system_prompt` is passed here — the model receives it as its first
instruction on every query. It defines the model's role:
`"You are a helpful assistant specializing in code and datasheets."`

`top_p=0.9` — nucleus sampling. The model only considers tokens
that together account for 90% of the probability mass.
This avoids very unlikely (and often wrong) word choices.

---

## Loading ChromaDB

```python
chroma_client     = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION)
total_chunks      = chroma_collection.count()
```
Opens the database created by `rag_ingest_recursive.py`.
`chroma_collection.count()` tells us how many chunks are stored.
If it's 0, we haven't ingested anything yet — script exits with a warning.

```python
vector_store    = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index           = VectorStoreIndex.from_vector_store(
    vector_store,
    storage_context=storage_context
)
```

`VectorStoreIndex.from_vector_store()` — loads the existing index
from ChromaDB. Note: `from_vector_store` (loading) vs `from_documents`
(creating). We're loading here, not re-ingesting.

---

## Session file

```python
os.makedirs("output", exist_ok=True)
_ts          = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
SESSION_FILE = f"output/rag_session_{_ts}.md"
```
One file per session, named with the timestamp.
Every Q&A is appended to this file throughout the session.

---

## Chat engine

```python
memory = ChatMemoryBuffer.from_defaults(token_limit=HISTORY_BUFFER)

chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    memory=memory,
    similarity_top_k=TOP_K,
    system_prompt=SYSTEM_PROMPT,
    streaming=True,
)
```

### chat_mode="condense_plus_context" explained

This mode does two things on every question:

**Step 1 — Condense** (the "condense" part):
The model rewrites your question to be self-contained,
incorporating relevant history.

```
History:     "Q: What chip are we using? A: The ADXL362."
Question:    "How do I init it?"
              ↓ condensed to:
             "How do I initialise the ADXL362?"
```

This produces a much better ChromaDB search query.

**Step 2 — Context** (the "context" part):
Uses the condensed question to search ChromaDB → retrieves TOP_K chunks →
injects them as context before sending to the LLM.

```
[system prompt]
[retrieved chunk 1: ADXL362 datasheet section 3.2]
[retrieved chunk 2: spi_adxl362_init() from source code]
[retrieved chunk 3: register map header file]
[condensed question: How do I initialise the ADXL362?]
        ↓
LLM answer based on YOUR documents
```

### Why not simpler modes?

| Mode | What it does | Problem |
|------|-------------|---------|
| `"context"` | RAG + history | follow-up questions search poorly |
| `"condense_plus_context"` | rewrites Q + RAG + history | best accuracy |

---

## query() function

```python
def query(question):
    print(f"\n🔍 {question}")
    print("-" * 70)
```
Shows what question is being processed.

```python
    response = chat_engine.stream_chat(question)
```
`stream_chat` returns immediately and gives you a generator.
Internally it:
1. Condenses the question using history
2. Searches ChromaDB
3. Builds the full prompt
4. Starts streaming from Ollama

```python
    result = ""
    for token in response.response_gen:
        print(token, end="", flush=True)
        result += token
```
`response.response_gen` is a generator — yields one token at a time.
We print each token immediately (`flush=True`) and accumulate them
into `result` for saving to the session file.

```python
    with open(SESSION_FILE, "a") as f:
        f.write(f"**Q:** {question}\n\n{result}\n\n---\n\n")
```
`"a"` mode — append, never overwrite. Each Q&A is added to the end.
The session file grows throughout the conversation.

---

## main() — interactive mode

```python
print("Paste text (. to finish, /bye to exit):")
lines = []
while True:
    line = input(">>> ")
    if line.strip() == ".":
        break
    if line.strip() == "/bye":
        sys.exit(0)
    lines.append(line)
q = "\n".join(lines).strip()
```
Multi-line input — same pattern as chat.py.
Type `.` alone on a line to send. Paste as many lines as needed.
`">>> "` prompt makes it visually clear you're in input mode.

### Commands

```python
if q == "/history":
    msgs = chat_engine.chat_history
    for i in range(0, len(msgs) - 1, 2):
        print(f"  Q{i//2+1}: {msgs[i].content}")
        preview = msgs[i+1].content[:100]
        print(f"  A{i//2+1}: {preview}...")
```
`chat_engine.chat_history` — the list of all messages stored internally.
Messages alternate: user, assistant, user, assistant...
`range(0, len-1, 2)` steps through in pairs: indices 0,2,4,6...

```python
if q == "/clear":
    chat_engine.reset()
    query_count = 0
    print("✓ History cleared")
```
`chat_engine.reset()` — clears the ChatMemoryBuffer.
The model starts fresh with no conversation memory.
The ChromaDB index is NOT cleared — your documents are still there.

---

## command-line mode

```python
else:
    query(" ".join(sys.argv[1:]))
```
If you pass arguments when running the script:
```bash
python3 rag_query4.py "What is the SPI init sequence?"
```
`sys.argv` = `["rag_query4.py", "What", "is", "the", "SPI", "init", "sequence?"]`
`sys.argv[1:]` = `["What", "is", "the", ...]`
`" ".join(...)` = `"What is the SPI init sequence?"`

Useful for scripting or quick one-off questions.

---

## Full data flow

```
rag_query4.py starts
        ↓
connect to ChromaDB → load index
        ↓
create chat_engine with memory + RAG + streaming
        ↓
while True:
  collect multi-line input
        ↓
  chat_engine.stream_chat(question)
        ↓
  [condense question using history]   ← 1 extra LLM call
        ↓
  [embed condensed Q → vector]        ← nomic-embed-text
        ↓
  [search ChromaDB → TOP_K chunks]    ← vector similarity search
        ↓
  [system + history + chunks + Q → Ollama]
        ↓
  stream reply token by token to screen
        ↓
  append Q&A to output/rag_session_TIMESTAMP.md
        ↓
  store reply in ChatMemoryBuffer
        ↓
next question...
```

---

## Comparison with chat.py

| Feature | chat.py | rag_query4.py |
|---------|---------|--------------|
| Document search | ❌ | ✅ ChromaDB |
| Conversation memory | ✅ | ✅ |
| Streaming | ✅ | ✅ |
| Session save | ✅ | ✅ |
| /history command | ❌ | ✅ |
| /clear command | ❌ | ✅ |
| Multi-line input | ✅ | ✅ |
| Use case | general chat | code/doc Q&A |

---

*Guide written April 2026*
