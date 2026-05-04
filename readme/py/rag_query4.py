#!/usr/bin/env python3
"""
RAG Query 4 — Ask questions about your ingested code/datasheets
===============================================================

Uses LlamaIndex chat_engine (chat_mode="condense_plus_context"):
  - RAG: retrieves relevant chunks from ChromaDB on every question
  - Chat: maintains role/content history automatically
  - Streaming: token by token output

Usage:
    python3 rag_query4.py "What is the SPI command to read a register?"
    python3 rag_query4.py        # interactive mode
"""

import datetime
import sys
import os
import chromadb
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

OLLAMA_URL         = "http://10.0.0.38:11434"
LLM_MODEL          = "qwen2.5-coder:7b"
EMBED_MODEL        = "nomic-embed-text"
CHROMA_PATH        = "./chroma_db"
COLLECTION         = "code_files"

TEMPERATURE        = 0.2
NUM_PREDICT        = 512
TOP_P              = 0.9
TOP_K              = 5
MAX_CONTEXT_WINDOW = 8192

SYSTEM_PROMPT = """You are a helpful assistant specializing in code, datasheets, and technical documentation.
You provide clear, concise answers with practical examples.
When referencing code, include file names and line numbers when possible."""

# Tokens reserved for conversation history.
# Rule: MAX_CONTEXT_WINDOW - system_prompt - RAG chunks - NUM_PREDICT - question
# For 8192 context: 8192 - 512 - 2000 - 512 - 512 = ~4500 safe maximum.
# Increase if your model has a larger context window (e.g. 100000 for Llama 3.1 128k).
HISTORY_BUFFER = 4500


# ════════════════════════════════════════════════════════════════════════════
# SETUP
# ════════════════════════════════════════════════════════════════════════════

print("⚙️  Setting up LLM and embeddings...")

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

Settings.embed_model = OllamaEmbedding(
    model_name=EMBED_MODEL,
    base_url=OLLAMA_URL
)

print("✓ LLM configured")

# ── Load vector database ──────────────────────────────────────────────────
print(f"📚 Loading vector database from: {CHROMA_PATH}")

try:
    chroma_client     = chromadb.PersistentClient(path=CHROMA_PATH)
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION)
    total_chunks      = chroma_collection.count()
    print(f"✓ Loaded {total_chunks} chunks")

    if total_chunks == 0:
        print("⚠️  No data in database! Run ingest first:")
        print("   python3 rag_ingest_recursive.py /path/to/code/")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error loading database: {e}")
    sys.exit(1)

vector_store    = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index           = VectorStoreIndex.from_vector_store(
    vector_store,
    storage_context=storage_context
)

print("✓ Index ready\n")

# ── Session log — one file per run, timestamped ───────────────────────────
os.makedirs("output", exist_ok=True)
_ts          = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
SESSION_FILE = f"output/rag_session_{_ts}.md"

# ── Chat engine — RAG + role/content history, created once per session ────
# chat_mode="condense_plus_context":
#   - retrieves TOP_K relevant chunks from ChromaDB on every question (RAG)
#   - maintains conversation history in role/content format automatically
from llama_index.core.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(token_limit=HISTORY_BUFFER)

chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    memory=memory,
    similarity_top_k=TOP_K,
    system_prompt=SYSTEM_PROMPT,
    streaming=True,
)


# ════════════════════════════════════════════════════════════════════════════
# QUERY FUNCTION
# ════════════════════════════════════════════════════════════════════════════

def query(question):
    """
    Send question to chat engine.
    chat_engine handles RAG retrieval and history internally.
    Returns answer string or None on error.
    """
    print(f"\n🔍 {question}")
    print("-" * 70)

    try:
        response = chat_engine.stream_chat(question)

        result = ""
        for token in response.response_gen:
            print(token, end="", flush=True)
            result += token

        print("\n" + "-" * 70)

        # append Q&A to session log
        with open(SESSION_FILE, "a") as f:
            f.write(f"**Q:** {question}\n\n{result}\n\n---\n\n")

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    """
    Two modes:
    1. No arguments  → interactive mode
    2. Arguments     → one question then exit
    """

    if len(sys.argv) < 2:
        # ── INTERACTIVE MODE ──────────────────────────────────────────────
        print("=" * 70)
        print("🤖 RAG Query 4 — Interactive Mode")
        print(f"📄 Session log: {SESSION_FILE}")
        print("=" * 70)
        print("Terminate input with '.' on its own line.")
        print("Commands: /history  /clear  /help  /bye")
        print("=" * 70)

        query_count = 0

        while True:
            try:
                print("Paste text (. to finish, /bye to exit):")
                lines = []

                while True:
                    line = input(">>> ")
                    if line.strip() == ".":
                        break
                    if line.strip() == "/bye":
                        print(f"\n👋 Goodbye! {query_count} queries. Log: {SESSION_FILE}")
                        sys.exit(0)
                    lines.append(line)

                q = "\n".join(lines).strip()

                if q.lower() in ["/bye", "bye", "/exit", "exit", "quit"]:
                    print(f"\n👋 Goodbye! {query_count} queries. Log: {SESSION_FILE}")
                    break

                if not q:
                    continue

                if q == "/history":
                    # chat_engine stores history internally
                    msgs = chat_engine.chat_history
                    if msgs:
                        print(f"\n📚 History ({len(msgs)//2} exchanges):")
                        for i in range(0, len(msgs) - 1, 2):
                            print(f"\n  Q{i//2+1}: {msgs[i].content}")
                            preview = msgs[i+1].content[:100]
                            print(f"  A{i//2+1}: {preview}...")
                    else:
                        print("\n📚 No history yet")
                    continue

                if q == "/clear":
                    chat_engine.reset()
                    query_count = 0
                    print("✓ History cleared")
                    continue

                if q == "/help":
                    print("\n📖 Commands:")
                    print("   /history  — show conversation history")
                    print("   /clear    — clear history")
                    print("   /help     — this help")
                    print("   /bye      — exit")
                    continue

                answer = query(q)
                if answer:
                    query_count += 1
                    print(f"   [Memory: {query_count} exchanges]")

            except Exception as e:
                print(f"❌ Error: {e}")

    else:
        # ── COMMAND-LINE MODE ─────────────────────────────────────────────
        query(" ".join(sys.argv[1:]))


if __name__ == "__main__":
    main()
