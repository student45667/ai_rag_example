#!/usr/bin/env python3
"""
RAG Query — Ask questions about your ingested code/datasheets
==============================================================

Retrieves relevant chunks from ChromaDB, sends to Ollama for answer.

Usage:
    python3 rag_query.py "What is the SPI command to read a register?"
    python3 rag_query.py "List all register addresses"
    python3 rag_query.py "Write an init function for the ADXL362"
    
    # Interactive mode (no arguments)
    python3 rag_query.py
"""

import datetime
import sys
import os
from pathlib import Path
import chromadb
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

OLLAMA_URL = "http://10.0.0.38:11434"  # ← Change to your Linux IP
LLM_MODEL = "qwen2.5-coder:7b"
EMBED_MODEL = "nomic-embed-text"
CHROMA_PATH = "./chroma_db"
COLLECTION = "code_files"

# ────────────────────────────────────────────────────────────────────────────
# LLM Settings — Control how the language model responds
# ────────────────────────────────────────────────────────────────────────────

TEMPERATURE = 0.5
# Controls response creativity/randomness (range: 0.0 to 2.0)
#   0.1-0.3  = Very focused, deterministic (best for code & technical Q&A)
#   0.5      = Balanced (default - good for general use)
#   0.7-1.0  = More creative, varied responses
#   1.5-2.0  = Very creative, may be inaccurate
# Example: For datasheet questions, use 0.2-0.3 for precise answers

NUM_PREDICT = 512
# Maximum tokens (words) in the response (range: 1 to 4096)
#   128      = ~1-2 sentences (quick answers)
#   256      = ~2-4 sentences (short paragraph)
#   512      = ~4-8 sentences (medium answer) ← GOOD DEFAULT
#   1024     = ~1 full page (long detailed answer)
#   2048     = ~2 pages (comprehensive explanation)
# Note: Longer responses take more time and use more tokens

TOP_P = 0.9
# Nucleus sampling - controls diversity in word selection (range: 0.0 to 1.0)
#   0.5      = Only most probable words (less diverse)
#   0.9      = More diverse vocabulary (balanced) ← DEFAULT
#   1.0      = Maximum diversity (may be less coherent)
# How it works: Only consider words that collectively have TOP_P probability
# Example: TOP_P=0.9 means "use words that make up 90% of probability mass"

TOP_K = 5
# Number of document chunks to retrieve from vector database (range: 1 to 20)
#   1-2      = Only most relevant chunks (fast, focused)
#   3-5      = Standard balance (good for RAG) ← DEFAULT
#   5-10     = More context, broader search (slower but more thorough)
#   10+      = Comprehensive search (slow, may include noise)
# Note: Higher values increase search time but may improve answer quality
# Chunks are code files, datasheet sections, or documentation snippets

MAX_CONTEXT_WINDOW = 8192
# Maximum context window size for conversation history (range: 512 to 8192)
#   512      = Small (only last 1-2 questions)
#   1024     = Small-Medium (last 2-3 questions)
#   2048     = Medium (last 3-5 questions) ← DEFAULT
#   4096     = Large (last 5-10 questions)
#   8192     = Very Large (last 10+ questions - only if model supports it)
# How it works: Tracks conversation history up to this token limit
# Example: Set to 4096 to keep more conversation context
# Warning: Larger values = slower response times, more memory usage

# System prompt (optional)
SYSTEM_PROMPT = """You are a helpful assistant specializing in code, datasheets, and technical documentation.
You provide clear, concise answers with practical examples.
When referencing code, include file names and line numbers when possible."""


# ════════════════════════════════════════════════════════════════════════════
# SETUP LLM AND EMBEDDINGS
# ════════════════════════════════════════════════════════════════════════════

print("⚙️  Setting up LLM and embeddings...")

Settings.llm = Ollama(
    model=LLM_MODEL,
    base_url=OLLAMA_URL,
    request_timeout=600
)

Settings.embed_model = OllamaEmbedding(
    model_name=EMBED_MODEL,
    base_url=OLLAMA_URL
)

print("✓ LLM configured")


# ════════════════════════════════════════════════════════════════════════════
# LOAD VECTOR DATABASE
# ════════════════════════════════════════════════════════════════════════════

print(f"📚 Loading vector database from: {CHROMA_PATH}")

try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION)
    
    total_chunks = chroma_collection.count()
    print(f"✓ Loaded {total_chunks} chunks")
    
    if total_chunks == 0:
        print("⚠️  No data in database! Run ingest first:")
        print("   python3 rag_ingest_recursive.py /path/to/code/")
        sys.exit(1)
    
except Exception as e:
    print(f"❌ Error loading database: {e}")
    sys.exit(1)

# Create vector store and index
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(
    vector_store,
    storage_context=storage_context
)

print("✓ Index ready for queries\n")


# ════════════════════════════════════════════════════════════════════════════
# QUERY FUNCTION
# ════════════════════════════════════════════════════════════════════════════

def query(question, conversation_history=None):
    """
    Query the RAG database using configured settings with conversation context
    
    Flow:
    1. Build context from previous queries (if any)
    2. Calculate context window usage percentage
    3. Update LLM with settings (temperature, token limit, etc)
    4. Search vector database for TOP_K most relevant chunks
    5. Send question + previous context + chunks to LLM for better answer
    6. Stream response token-by-token
    7. Display source documents used
    8. Save full output to markdown file
    9. Return answer to update conversation history
    
    Args:
        question: User's current question to answer
        conversation_history: List of previous Q&A pairs for context
    Returns:
        answer: The model's response (for storing in conversation history)
    """
    
    # ── Build conversation context for the model ────────────────────────────────
    # If this is not the first question, include previous context
    context_str = ""
    context_tokens = 0
    
    if conversation_history and len(conversation_history) > 0:
        context_str = "\n### Previous Conversation Context:\n"
        # Last 3 questions only (to avoid context window explosion)
        for i, item in enumerate(conversation_history[-3:], 1):
            q_text = f"\nQ{i}: {item['question']}\nA{i}: {item['answer']}\n"
            context_str += q_text
            # Rough token estimate: ~1 token per 4 characters
            context_tokens += len(q_text) // 4
        context_str += "\n---\n\n"
    
    # Enhanced question with context
    enhanced_question = context_str + f"Current question: {question}"
    
    # ── Calculate context window usage ─────────────────────────────────────────
    # Estimate total tokens in context
    question_tokens = len(question) // 4  # Rough estimate
    total_input_tokens = context_tokens + question_tokens
    
    # MAX_CONTEXT_WINDOW depends on your model and hardware
    # Can be configured at top of script (see CONFIGURATION section)
    # NUM_PREDICT is for OUTPUT tokens, so input has more room
    MAX_CONTEXT_WINDOW = globals().get('MAX_CONTEXT_WINDOW', 2048)
    context_percentage = (total_input_tokens / MAX_CONTEXT_WINDOW) * 100
    context_percentage = min(context_percentage, 100)  # Cap at 100%
    
    # Create context bar visualization
    bar_length = 30
    filled = int((context_percentage / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    # Color coding for context usage
    if context_percentage < 30:
        context_status = "✓ LOW"
    elif context_percentage < 60:
        context_status = "⚠ MEDIUM"
    elif context_percentage < 85:
        context_status = "⚠ HIGH"
    else:
        context_status = "⚠⚠ CRITICAL"
    
    print(f"\n🔍 Query #{len(conversation_history) + 1 if conversation_history else 1}: {question}")
    
    if conversation_history:
        print(f"   📚 Context: {len(conversation_history)} previous Q&A pairs")
        print(f"   💾 Tokens: ~{total_input_tokens} / {MAX_CONTEXT_WINDOW} ({context_percentage:.1f}%)")
        print(f"   {bar} {context_status}")
        
        if context_percentage > 85:
            print(f"   ⚠️  Context window is {context_percentage:.1f}% full!")
            print(f"      Use /clear to reset history if needed")
    
    print("⏳ Searching...")
    
    try:
        # ── STEP 1: Configure LLM with settings ────────────────────────────────
        # This updates the language model with our configured parameters
        # Context window controls how much conversation history model can see
        Settings.llm = Ollama(
            model=LLM_MODEL,              # Which model to use (qwen2.5-coder)
            base_url=OLLAMA_URL,          # Where Ollama is running (Linux PC)
            request_timeout=600,          # Wait up to 600 seconds for response
            temperature=TEMPERATURE,      # Creativity level (0.5 = balanced)
            num_predict=NUM_PREDICT,      # Max tokens in response (512 = ~paragraph)
            top_p=TOP_P,                  # Diversity in word selection (0.9)
            context_window=MAX_CONTEXT_WINDOW,  # Context size for conversation history
        )
        
        # ── STEP 2: Create query engine ────────────────────────────────────────
        # This engine will search the vector database and call the LLM
        query_engine = index.as_query_engine(
            similarity_top_k=TOP_K,       # Retrieve TOP_K most similar chunks (5)
            streaming=True,               # Stream tokens one-by-one (not wait for full response)
        )
        
        # ── STEP 3: Execute the query ──────────────────────────────────────────
        # Vector database searches for similar chunks
        # Then sends to LLM with: previous context + current question + chunks
        # This allows the model to understand the conversation flow
        response = query_engine.query(enhanced_question)
        
        # ── STEP 4: Stream and display answer ──────────────────────────────────
        # Print answer as tokens arrive (like ChatGPT)
        print("\n📝 Answer:")
        print("-" * 70)
        
        result = ""
        for token in response.response_gen:
            # Print each token immediately (real-time streaming)
            print(token, end="", flush=True)
            # Collect all tokens for saving to file
            result += token
        
        print("\n" + "-" * 70)
        
        # ── STEP 5: Show which documents were used ────────────────────────────
        # Display source files and relevance scores (0.0-1.0)
        print(f"\n📚 Sources used ({len(response.source_nodes)} chunks):")
        for i, node in enumerate(response.source_nodes, 1):
            fname = node.metadata.get("filename", "unknown")     # Original file name
            ftype = node.metadata.get("type", "unknown")         # Type (code/text)
            score = node.score or 0                              # Relevance score
            rel_path = node.metadata.get("rel_path", fname)      # Relative path from root
            
            print(f"   {i}. {rel_path}")
            print(f"      Type: {ftype} | Relevance: {score:.3f}")
        
        # ── STEP 6: Save full output to markdown file ──────────────────────────
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # Generate filename with timestamp (e.g., query_20240501_143025.md)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = f"output/query_{ts}.md"
        
        # Build markdown content with question, answer, and sources
        output_content = f"""# Query Results
**Question:** {question}

**Timestamp:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Answer

{result}

---

## Sources

"""
        
        # Append all source files used to the markdown
        for i, node in enumerate(response.source_nodes, 1):
            fname = node.metadata.get("filename", "unknown")
            rel_path = node.metadata.get("rel_path", fname)
            score = node.score or 0
            output_content += f"\n{i}. **{rel_path}** (relevance: {score:.3f})\n"
        
        # Write to file
        with open(out_file, "w") as f:
            f.write(output_content)
        
        print(f"\n✅ Saved to: {out_file}\n")
        
        # Return the answer for storing in conversation history
        return result
        
    except Exception as e:
        # Error handling
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None  # Return None on error


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    """
    Main entry point for the RAG query system
    
    Two modes:
    1. No arguments → Interactive mode (ask multiple questions)
    2. Arguments → Command-line mode (answer one question and exit)
    
    Examples:
        python3 rag_query.py                        # Interactive mode
        python3 rag_query.py "What is the voltage?" # Command-line mode
    """
    
    if len(sys.argv) < 2:
        # ── INTERACTIVE MODE ──────────────────────────────────────────────────
        # User can ask multiple questions until they type '/bye'
        # Each question uses previous context for better answers
        print("=" * 70)
        print("🤖 RAG Query — Interactive Mode with Conversation Memory")
        print("=" * 70)
        print("Type your questions (type '/bye' to exit)")
        print("Note: Model remembers previous Q&A for better context")
        print("Examples:")
        print('  "What is the supply voltage?"')
        print('  "How do I use it?" ← References previous answer')
        print('  "Show me code examples" ← Understands full conversation')
        print("=" * 70)
        
        # Initialize conversation history to store Q&A pairs
        conversation_history = []
        query_count = 0
        
        # Keep asking until user exits
       # Keep asking until user exits
        while True:
            try:
                # ── Get user input (single or multi-line with /end terminator) ──
                print("=" * 70)
                print("Paste text (type /end to finish, /bye to exit):")
                lines = []
                
                while True:
                    line = input()
                    
                    # Check for terminator or exit command
                    if line.strip() == ".":
                        break
                    
                    if line.strip() == "/bye":
                        print("\n👋 Goodbye!")
                        print(f"Session ended. Total queries: {query_count}")
                        sys.exit(0)  # Exit immediately
                    
                    # Append line only if it's not a command
                    lines.append(line)
                
                # Join lines into single query
                q = "\n".join(lines)
                
                # Check for exit commands FIRST (before empty check!)
                if q.lower() in ['/bye', 'bye', '/exit', 'exit', 'quit']:
                    print("\n👋 Goodbye!")
                    print(f"Session ended. Total queries: {query_count}")
                    break
                
                # Skip if empty
                if not q.strip():
                    continue
  


                # Show conversation history status
                if q == '/history':
                    if conversation_history:
                        print(f"\n📚 Conversation History ({len(conversation_history)} Q&A pairs):")
                        for i, item in enumerate(conversation_history, 1):
                            print(f"\n  Q{i}: {item['question']}")
                            # Show first 100 chars of answer
                            answer_preview = item['answer'][:100] + "..." if len(item['answer']) > 100 else item['answer']
                            print(f"  A{i}: {answer_preview}")
                    else:
                        print("\n📚 No conversation history yet")
                    continue
                
                # Show help
                if q == '/help':
                    print("\n📖 Commands:")
                    print("   /history     - Show conversation history")
                    print("   /clear       - Clear conversation history")
                    print("   /help        - Show this help")
                    print("   /bye         - Exit")
                    print()
                    continue
                
                # Clear history if requested
                if q == '/clear':
                    conversation_history = []
                    query_count = 0
                    print("✓ Conversation history cleared")
                    continue
                
                # Process non-empty questions
                if q:
                    # Execute query WITH conversation history
                    answer = query(q, conversation_history=conversation_history)
                    
                    # Store Q&A in history for future context
                    if answer:  # Only store if answer was successful
                        conversation_history.append({
                            'question': q,
                            'answer': answer
                        })
                        query_count += 1
                        print(f"   [Stored in memory - Total: {query_count} queries]")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    


    
    else:
        # ── COMMAND-LINE MODE ────────────────────────────────────────────────
        # User provides question as argument, answer it, then exit
        # Combine all arguments into one question
        question = " ".join(sys.argv[1:])
        query(question)


if __name__ == "__main__":
    main()