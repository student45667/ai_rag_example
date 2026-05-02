# RAG Query - Complete Documentation

## Overview

`rag_query_3.py` is a **RAG (Retrieval-Augmented Generation) query script** that lets you ask questions about your ingested code and documents. It retrieves relevant information from the vector database and sends it to the language model for context-aware answers.

Think of it as:
- **Retriever**: Searches vector database for relevant chunks
- **Augmenter**: Combines retrieved chunks with your question
- **Generator**: Sends to LLM to generate answer
- **Memory**: Keeps track of conversation history
- **Tracker**: Shows context window usage

---

## Table of Contents

1. [Configuration Section](#configuration-section)
2. [Setup Phase](#setup-phase)
3. [Query Function](#query-function)
4. [Main Execution](#main-execution)
5. [Interactive Mode](#interactive-mode)
6. [How to Run](#how-to-run)
7. [Understanding Context Window](#understanding-context-window)
8. [Conversation Memory](#conversation-memory)
9. [Output Files](#output-files)
10. [Troubleshooting](#troubleshooting)

---

## Configuration Section

### Location
Lines 30-108 at the top of the script

### OLLAMA_URL
```python
OLLAMA_URL = "http://10.0.0.38:11434"
```

**What it does:**
- Tells script where Ollama is running
- IP: `10.0.0.38` (your Linux PC)
- Port: `11434` (default Ollama port)

**Change if:**
- Ollama on different machine
- Using different port

### LLM_MODEL
```python
LLM_MODEL = "qwen2.5-coder:7b"
```

**What it does:**
- Language model used to generate answers
- This model will answer your questions
- Must be installed in Ollama

**Used for:**
- Understanding your question
- Generating answer text
- Reasoning about code

### EMBED_MODEL
```python
EMBED_MODEL = "nomic-embed-text"
```

**What it does:**
- Embedding model for converting text to vectors
- Used to search vector database
- Must match what you used in ingestion

**Important:**
- Must be SAME as in `rag_ingest_recursive.py`
- Different embedding = can't find documents!

### CHROMA_PATH
```python
CHROMA_PATH = "./chroma_db"
```

**What it does:**
- Path to vector database
- Must be SAME as ingestion script
- Reads from database (not creates new)

**Example:**
```
Your project/
├─ rag_ingest_recursive.py
├─ rag_query_3.py
└─ chroma_db/              ← Read from here
```

### COLLECTION
```python
COLLECTION = "code_files"
```

**What it does:**
- Collection name in ChromaDB
- Must match ingestion script
- Retrieves from this collection

### MAX_CONTEXT_WINDOW
```python
MAX_CONTEXT_WINDOW = 32768
```

**What it does:**
- Maximum context tokens model can handle
- For display purposes (tracking usage)
- Based on your model's actual capacity

**Values:**
```python
2048      # Conservative (older models)
4096      # Standard (7B models)
8192      # Good (newer 7B)
16384     # Large (if model supports)
32768     # Very large (Qwen 2.5 Coder actual)
```

**How to find actual value:**
```bash
ollama show qwen2.5-coder:7b | grep "context length"
# Output: context length: 32768
```

### NUM_PREDICT
```python
NUM_PREDICT = 512
```

**What it does:**
- Maximum tokens in response
- Controls response length
- Saves context space for input

**Values:**
```python
128       # ~1-2 sentences (quick)
256       # ~2-4 sentences (short)
512       # ~4-8 sentences (medium) ← DEFAULT
1024      # ~1 full page (long)
2048      # ~2 pages (very long)
```

**Trade-off:**
```
Higher NUM_PREDICT:
  ✓ Longer answers
  ✓ More detailed
  ✗ Less context space for history
  ✗ Takes longer to generate

Lower NUM_PREDICT:
  ✓ Saves context space
  ✓ Faster responses
  ✗ Shorter answers
```

### TOP_P
```python
TOP_P = 0.9
```

**What it does:**
- Nucleus sampling (diversity control)
- How varied the response is
- Range: 0.0 to 1.0

**Values:**
```python
0.5       # Very focused (only probable words)
0.7       # Balanced (some variety)
0.9       # Diverse (good default)
1.0       # Maximum diversity
```

**For code questions:**
```python
TOP_P = 0.3    # Very focused (precise code)
```

**For creative questions:**
```python
TOP_P = 0.95   # More creative
```

### TOP_K
```python
TOP_K = 5
```

**What it does:**
- How many document chunks to retrieve
- From vector database search
- Range: 1-20

**Values:**
```python
1-2       # Only most relevant (fast)
3-5       # Standard balance (good) ← DEFAULT
5-10      # Thorough (slower)
10+       # Comprehensive (very slow)
```

**Trade-off:**
```
Higher TOP_K:
  ✓ More context from documents
  ✓ Better answers
  ✗ Slower search
  ✗ More tokens used

Lower TOP_K:
  ✓ Faster search
  ✓ Saves tokens
  ✗ Less context
```

### TEMPERATURE
```python
TEMPERATURE = 0.5
```

**What it does:**
- Creativity/randomness level
- Range: 0.0 to 2.0

**Values:**
```python
0.1-0.3   # Very focused (code answers)
0.5       # Balanced (good default)
0.7-1.0   # Creative (explanations)
1.5+      # Very creative (risky)
```

**For datasheet questions:**
```python
TEMPERATURE = 0.2    # Precise, factual
```

**For explanations:**
```python
TEMPERATURE = 0.7    # More natural
```

---

## Setup Phase

### What Happens First

Before any queries, script initializes three things:

#### 1. Setup LLM and Embeddings (Lines 120-130)

```python
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
```

**`Settings.llm = Ollama(...)`**
- Connects to language model
- `model`: Which model to use
- `base_url`: Where Ollama runs
- `request_timeout=600`: Wait max 600 seconds

**`Settings.embed_model = OllamaEmbedding(...)`**
- Connects to embedding model
- For searching vector database
- Converts queries to vectors

#### 2. Load Vector Database (Lines 137-155)

```python
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
```

**`chromadb.PersistentClient(path=CHROMA_PATH)`**
- Loads existing database
- Must be created by ingest script first
- Raises error if not found

**`get_or_create_collection(COLLECTION)`**
- Gets collection named "code_files"
- Must match ingest script

**`chroma_collection.count()`**
- Counts chunks in database
- 0 = empty database (error)
- 156 = 156 chunks ready to search

#### 3. Create Vector Index (Lines 158-162)

```python
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(
    vector_store,
    storage_context=storage_context
)

print("✓ Index ready for queries\n")
```

**`ChromaVectorStore(chroma_collection=chroma_collection)`**
- Wraps ChromaDB for LlamaIndex
- Handles vector operations

**`VectorStoreIndex.from_vector_store(...)`**
- Creates queryable index
- Can search vectors
- Can fetch documents

---

## Query Function

### Location
Lines 169-331

### Function Signature
```python
def query(question, conversation_history=None):
```

### Parameters

**`question`** (str)
- User's question or code to analyze
- Example: `"What is the supply voltage?"`
- Example: `"void init() { ... }"`

**`conversation_history`** (list or None)
- Previous Q&A pairs for context
- Example:
  ```python
  [
    {"question": "What is ADXL362?", "answer": "It's a 3-axis..."},
    {"question": "How to use it?", "answer": "First configure..."}
  ]
  ```
- `None` = first query, no history

### Phase 1: Build Conversation Context

```python
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
```

**What it does:**
- Builds string with previous Q&A
- Only uses LAST 3 pairs (to save context)
- Estimates tokens used

**Why last 3 pairs?**
```
With 32K context window:
- If keep all 20 pairs = 4000+ tokens
- With last 3 pairs = ~500 tokens
- More room for current question + answer

The farther back, less relevant anyway!
```

**Token estimation:**
```python
context_tokens += len(q_text) // 4
```

**Why divide by 4?**
- Rough approximation: 1 token ≈ 4 characters
- 100 characters ≈ 25 tokens
- Used for display only (not exact)

### Phase 2: Create Enhanced Question

```python
enhanced_question = context_str + f"Current question: {question}"
```

**What it does:**
- Combines context with new question
- Model sees full conversation

**Example:**
```
### Previous Conversation Context:

Q1: What is the ADXL362?
A1: The ADXL362 is a 3-axis MEMS accelerometer...

Q2: What are pin functions?
A2: Pin 1 is VDD_IO, Pin 14 is VS...

---

Current question: How do I configure activity detection?
```

**Why important?**
- Model understands context
- Can reference previous answers
- Better responses

### Phase 3: Calculate Context Window Usage

```python
question_tokens = len(question) // 4
total_input_tokens = context_tokens + question_tokens

MAX_CONTEXT_WINDOW = 32768
context_percentage = (total_input_tokens / MAX_CONTEXT_WINDOW) * 100
context_percentage = min(context_percentage, 100)

# Create context bar visualization
bar_length = 30
filled = int((context_percentage / 100) * bar_length)
bar = "█" * filled + "░" * (bar_length - filled)
```

**Breaking it down:**

**`question_tokens = len(question) // 4`**
- Estimates tokens in current question
- Example: 100 character question ≈ 25 tokens

**`total_input_tokens = context_tokens + question_tokens`**
- Sum of all input tokens
- What actually goes to model

**`context_percentage = (total_input_tokens / MAX_CONTEXT_WINDOW) * 100`**
- Calculates percentage used
- Example: 3200 / 32768 = 9.8%

**`min(context_percentage, 100)`**
- Caps at 100% (never shows 101%)

**Bar visualization:**
```python
bar_length = 30                              # 30 characters wide
filled = int((9.8 / 100) * 30)             # 3 filled
bar = "█" * 3 + "░" * 27                   # "███░░░░░░░░░░░░░░░░░░░░░░░░░"
```

### Phase 4: Status Indicators

```python
if context_percentage < 30:
    context_status = "✓ LOW"
elif context_percentage < 60:
    context_status = "⚠ MEDIUM"
elif context_percentage < 85:
    context_status = "⚠ HIGH"
else:
    context_status = "⚠⚠ CRITICAL"
```

**Status meanings:**

| Range | Status | Meaning |
|-------|--------|---------|
| 0-30% | ✓ LOW | Plenty of space |
| 30-60% | ⚠ MEDIUM | Good, but watch it |
| 60-85% | ⚠ HIGH | Getting full |
| 85%+ | ⚠⚠ CRITICAL | Almost full |

### Phase 5: Display Status

```python
print(f"\n🔍 Query #{len(conversation_history) + 1 if conversation_history else 1}: {question}")

if conversation_history:
    print(f"   📚 Context: {len(conversation_history)} previous Q&A pairs")
    print(f"   💾 Tokens: ~{total_input_tokens} / {MAX_CONTEXT_WINDOW} ({context_percentage:.1f}%)")
    print(f"   {bar} {context_status}")
    
    if context_percentage > 85:
        print(f"   ⚠️  Context window is {context_percentage:.1f}% full!")
        print(f"      Use /clear to reset history if needed")
```

**Example output:**
```
🔍 Query #3: How do I configure activity detection?
   📚 Context: 2 previous Q&A pairs
   💾 Tokens: ~480 / 32768 (1.5%)
   ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ✓ LOW
```

### Phase 6: Configure LLM Settings

```python
Settings.llm = Ollama(
    model=LLM_MODEL,
    base_url=OLLAMA_URL,
    request_timeout=600,
    temperature=TEMPERATURE,
    num_predict=NUM_PREDICT,
    top_p=TOP_P,
)
```

**What it does:**
- Updates LLM with configured settings
- Sets temperature, token limit, etc.
- Happens for EVERY query (fresh settings)

**Why every query?**
- Could theoretically change settings between queries
- Ensures consistent settings

### Phase 7: Create Query Engine

```python
query_engine = index.as_query_engine(
    similarity_top_k=TOP_K,
    streaming=True,
)
```

**`index.as_query_engine(...)`**
- Creates engine that searches vectors
- Searches vector database
- Retrieves TOP_K most similar chunks

**`similarity_top_k=TOP_K`**
- How many chunks to retrieve
- Default: 5 chunks
- Top_k=3: Search returns 3 best matches

**`streaming=True`**
- Stream response token-by-token
- Like ChatGPT (word by word)
- Not wait for full response

### Phase 8: Execute Query

```python
response = query_engine.query(enhanced_question)
```

**What happens internally:**
1. Converts question to vector
2. Searches vector database
3. Finds TOP_K most similar chunks
4. Sends chunks + question to LLM
5. LLM generates answer
6. Returns response object

**Response contains:**
```python
response.response_gen         # Generator (tokens)
response.source_nodes        # Retrieved documents
response.source_nodes[i].score   # Relevance score
```

### Phase 9: Stream Response

```python
print("\n📝 Answer:")
print("-" * 70)

result = ""
for token in response.response_gen:
    print(token, end="", flush=True)
    result += token

print("\n" + "-" * 70)
```

**Breaking it down:**

**`for token in response.response_gen`**
- Iterates through response tokens
- Gets one word/token at a time
- Like streaming API

**`print(token, end="", flush=True)`**
- Print token without newline
- `flush=True`: Print immediately (not buffered)
- Shows response as it generates

**`result += token`**
- Collect all tokens
- Store for saving to file

**Example output:**
```
📝 Answer:
----------------------------------------------------------------------
The ADXL362 supply voltage range is 1.6V to 3.5V, making it suitable
for battery-powered applications. It supports low-power modes with
current consumption as low as 1.8µA at 100Hz.
----------------------------------------------------------------------
```

### Phase 10: Display Sources

```python
print(f"\n📚 Sources used ({len(response.source_nodes)} chunks):")
for i, node in enumerate(response.source_nodes, 1):
    fname = node.metadata.get("filename", "unknown")
    ftype = node.metadata.get("type", "unknown")
    score = node.score or 0
    rel_path = node.metadata.get("rel_path", fname)
    
    print(f"   {i}. {rel_path}")
    print(f"      Type: {ftype} | Relevance: {score:.3f}")
```

**What it shows:**
- Which documents were used
- Relevance score (0.0-1.0)
  - 1.0 = perfect match
  - 0.0 = no match

**Example output:**
```
📚 Sources used (5 chunks):
   1. hardware/esp32/variants/pins.h
      Type: code | Relevance: 0.875
   2. docs/ADXL362_datasheet.md
      Type: text | Relevance: 0.823
   3. src/sensor_config.cpp
      Type: code | Relevance: 0.756
```

### Phase 11: Save to File

```python
os.makedirs("output", exist_ok=True)
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
out_file = f"output/query_{ts}.md"

output_content = f"""# Query Results
**Question:** {question}

**Timestamp:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Answer

{result}

---

## Sources

"""

for i, node in enumerate(response.source_nodes, 1):
    fname = node.metadata.get("filename", "unknown")
    rel_path = node.metadata.get("rel_path", fname)
    score = node.score or 0
    output_content += f"\n{i}. **{rel_path}** (relevance: {score:.3f})\n"

with open(out_file, "w") as f:
    f.write(output_content)

print(f"\n✅ Saved to: {out_file}\n")
```

**What it does:**
- Creates markdown file with results
- Includes question, answer, sources
- Timestamped (no overwrites)

**File location:**
```
./output/
├─ query_20240501_143025.md
├─ query_20240501_143026.md
└─ query_20240501_143027.md
```

**File content:**
```markdown
# Query Results
**Question:** What is the supply voltage?

**Timestamp:** 2024-05-01 14:30:25

---

## Answer

The ADXL362 supply voltage range is 1.6V to 3.5V...

---

## Sources

1. **hardware/esp32/variants/pins.h** (relevance: 0.875)
2. **docs/ADXL362_datasheet.md** (relevance: 0.823)
```

### Phase 12: Return Answer

```python
return result
```

**What it returns:**
- Complete answer text
- Used to store in conversation history
- None if error occurred

---

## Main Execution

### Location
Lines 338-421

### Function Signature
```python
def main():
```

### Check for Command-Line Arguments

```python
if len(sys.argv) < 2:
    # INTERACTIVE MODE
else:
    # COMMAND-LINE MODE
```

**Two modes:**

1. **Interactive Mode** (no arguments)
   ```bash
   python3 rag_query_3.py
   # Ask multiple questions, use commands
   ```

2. **Command-Line Mode** (with arguments)
   ```bash
   python3 rag_query_3.py "What is supply voltage?"
   # One question, exit
   ```

---

## Interactive Mode

### Location
Lines 338-420

### Initialization

```python
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

conversation_history = []
query_count = 0
```

**What it shows:**
- Welcome message
- Instructions
- Examples of multi-turn queries

**Variables:**
- `conversation_history`: List of Q&A pairs
- `query_count`: Counter of processed queries

### Input Loop

```python
while True:
    try:
        print("=" * 70)
        print("Paste text (type /end to finish, /bye to exit):")
        lines = []
        
        while True:
            line = input()
            
            if line.strip() == "/end":
                break
            
            if line.strip() == "/bye":
                print("\n👋 Goodbye!")
                print(f"Session ended. Total queries: {query_count}")
                sys.exit(0)
            
            lines.append(line)
```

**Outer loop:** Main query loop (infinite until `/bye`)

**Inner loop:** Input collection loop
- Collects multiple lines
- Ends on `/end`
- Can exit on `/bye`

**`line.strip() == "/end"`**
- Exact terminator command
- Signals end of input

**`line.strip() == "/bye"`**
- Exit command in input loop
- Exits immediately

### Process Input

```python
q = "\n".join(lines)

if not q.strip():
    continue
```

**`"\n".join(lines)`**
- Joins lines with newlines
- Example:
  ```python
  lines = ["void init() {", "  delay(100);", "}"]
  q = "void init() {\n  delay(100);\n}"
  ```

**`if not q.strip(): continue`**
- Skip if empty
- Allows multiple blank presses

### Check for Exit Commands

```python
if q.lower() in ['/bye', 'bye', '/exit', 'exit', 'quit']:
    print("\n👋 Goodbye!")
    print(f"Session ended. Total queries: {query_count}")
    break
```

**Why multiple variations?**
- Users might forget slash
- `bye` or `/bye` both work
- `exit`, `quit` also work

### Check for Special Commands

#### /history Command

```python
if q == '/history':
    if conversation_history:
        print(f"\n📚 Conversation History ({len(conversation_history)} Q&A pairs):")
        for i, item in enumerate(conversation_history, 1):
            print(f"\n  Q{i}: {item['question']}")
            answer_preview = item['answer'][:100] + "..." if len(item['answer']) > 100 else item['answer']
            print(f"  A{i}: {answer_preview}")
    else:
        print("\n📚 No conversation history yet")
    continue
```

**What it shows:**
- All previous questions and answers
- Truncates answers to 100 chars
- Shows count of pairs

**Example output:**
```
📚 Conversation History (3 Q&A pairs):

  Q1: What is the ADXL362?
  A1: The ADXL362 is a 3-axis MEMS accelerometer with ultra-low power...

  Q2: What are the pin functions?
  A2: Pin 1 is VDD_IO, Pin 14 is VSENSE, Pin 13 is VS...

  Q3: How do I initialize it?
  A3: First, configure the control registers at 0x20 (POWER_CTL)...
```

#### /help Command

```python
if q == '/help':
    print("\n📖 Commands:")
    print("   /history     - Show conversation history")
    print("   /clear       - Clear conversation history")
    print("   /help        - Show this help")
    print("   /bye         - Exit")
    print()
    continue
```

**Shows:**
- All available commands
- Brief descriptions

#### /clear Command

```python
if q == '/clear':
    conversation_history = []
    query_count = 0
    print("✓ Conversation history cleared")
    continue
```

**What it does:**
- Empties conversation history
- Resets query counter
- Next query starts fresh

### Process Normal Query

```python
if q:
    answer = query(q, conversation_history=conversation_history)
    
    if answer:
        conversation_history.append({
            'question': q,
            'answer': answer
        })
        query_count += 1
        print(f"   [Stored in memory - Total: {query_count} queries]")
```

**Execution flow:**
1. Call `query()` with question and history
2. Get back answer text
3. If successful, store in history
4. Increment counter
5. Show confirmation

**Why check `if answer`?**
- `None` if error occurred
- Only store successful queries
- Bad answer won't poison history

---

## How to Run

### Interactive Mode

```bash
python3 rag_query_3.py
```

**First run:**
```
======================================================================
⚙️  Setting up LLM and embeddings...
✓ LLM and embeddings configured
📚 Loading vector database from: ./chroma_db
✓ Loaded 156 chunks
✓ Index ready for queries

======================================================================
🤖 RAG Query — Interactive Mode with Conversation Memory
======================================================================
Type your questions (type '/bye' to exit)
Note: Model remembers previous Q&A for better context
...
```

**Ask questions:**
```
======================================================================
Paste text (type /end to finish, /bye to exit):
What is the supply voltage of ADXL362?
/end

🔍 Query #1: What is the supply voltage of ADXL362?
   📚 Context: 0 previous Q&A pairs
⏳ Searching...

📝 Answer:
----------------------------------------------------------------------
The ADXL362 supply voltage range is 1.6V to 3.5V...
----------------------------------------------------------------------

📚 Sources used (3 chunks):
   1. docs/ADXL362_datasheet.md
      Type: text | Relevance: 0.892
   2. src/sensor.cpp
      Type: code | Relevance: 0.756
   3. config/pins.h
      Type: code | Relevance: 0.634

✅ Saved to: output/query_20240501_143025.md
   [Stored in memory - Total: 1 queries]
```

**Follow-up question:**
```
======================================================================
Paste text (type /end to finish, /bye to exit):
How do I configure it?
/end

🔍 Query #2: How do I configure it?
   📚 Context: 1 previous Q&A pairs
   💾 Tokens: ~480 / 32768 (1.5%)
   ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ✓ LOW
⏳ Searching...

📝 Answer:
----------------------------------------------------------------------
To configure the ADXL362, which we discussed operates at 1.6V-3.5V,
you need to:
1. Initialize SPI interface
2. Configure POWER_CTL register at 0x20...
----------------------------------------------------------------------
```

### Command-Line Mode

```bash
python3 rag_query_3.py "What is the supply voltage?"
```

**Output:**
```
🔍 Query #1: What is the supply voltage?
⏳ Searching...

📝 Answer:
The ADXL362 supply voltage range is 1.6V to 3.5V...

✅ Saved to: output/query_20240501_143025.md
```

Then exits immediately.

### Common Workflows

**Quick single question:**
```bash
python3 rag_query_3.py "How to initialize?"
```

**Long research session:**
```bash
python3 rag_query_3.py
# Ask 10+ questions with context
# Use /history to review
# Type /bye to exit
```

**Clear history between topics:**
```bash
# In script:
/clear
# Now asks about new topic without old context
```

---

## Understanding Context Window

### What is Context Window?

```
Context Window = Total tokens model can process

Example for Qwen 2.5 Coder:
├─ Input tokens:   ~24,000 (question + history + chunks)
├─ Output tokens:  ~512 (response, NUM_PREDICT)
└─ Total:          ~32,768 (context window size)
```

### Token Usage Breakdown

```
32,768 total tokens

Input side (what goes to model):
├─ Conversation history:     ~2,000 tokens
├─ Retrieved chunks (TOP_K=5): ~5,000 tokens
├─ Current question:          ~500 tokens
└─ System prompt:             ~200 tokens
   Subtotal: ~7,700 tokens

Output side:
└─ NUM_PREDICT (response):   ~512 tokens

Remaining buffer: ~24,556 tokens (safety)
```

### Why Track Usage?

```
If context > 100%:
❌ Query fails
❌ Can't send to model
❌ Error: "input exceeds context"

If context > 85%:
⚠️ Getting close to limit
⚠️ Might fail soon
⚠️ Use /clear to reset
```

### How to See Real Usage

Currently shown as estimate (rough):
```python
context_percentage = (total_input_tokens / MAX_CONTEXT_WINDOW) * 100
```

More accurate would be:
```python
# Use actual token counter
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("...")
actual_tokens = len(tokenizer.encode(enhanced_question))
```

But estimate is good enough!

---

## Conversation Memory

### How It Works

**Query 1:**
```
Input: "What is ADXL362?"
Model answers, response stored
History = [Q1: "...", A1: "..."]
```

**Query 2:**
```
Input to model:
  ### Previous Conversation Context:
  Q1: What is ADXL362?
  A1: It's a 3-axis...
  ---
  Current question: How to configure it?

Model sees both → Better answer!
History = [Q1: "...", A1: "...", Q2: "...", A2: "..."]
```

### Conversation History Storage

```python
conversation_history = [
    {
        'question': 'What is the supply voltage?',
        'answer': 'The ADXL362 supply voltage range is 1.6V to 3.5V...'
    },
    {
        'question': 'How do I use it?',
        'answer': 'First, configure the control registers at 0x20...'
    },
]
```

### Limiting to Last 3

```python
for i, item in enumerate(conversation_history[-3:], 1):
    # Only process last 3 items
```

**Why?**
- Keep context under control
- Most recent most relevant
- Older questions less important
- Saves token space

**Example:**
```python
history = [Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10]
history[-3:] = [Q8, Q9, Q10]  # Only these 3 sent
```

### Commands to Manage History

| Command | What it does |
|---------|-------------|
| `/history` | Show all Q&A pairs |
| `/clear` | Delete all history, start fresh |
| `/bye` | Exit program |

---

## Output Files

### Location
```
./output/
├─ query_20240501_143025.md
├─ query_20240501_143026.md
└─ query_20240501_143027.md
```

### File Format

```markdown
# Query Results
**Question:** What is the supply voltage?

**Timestamp:** 2024-05-01 14:30:25

---

## Answer

The ADXL362 supply voltage range is 1.6V to 3.5V, suitable for
battery-powered applications. It consumes as little as 1.8µA at 100Hz.

---

## Sources

1. **docs/ADXL362_datasheet.md** (relevance: 0.892)
2. **src/sensor.cpp** (relevance: 0.756)
3. **config/pins.h** (relevance: 0.634)
```

### Filename Format

```
query_YYYYMMDD_HHMMSS.md
       │      │ │  │ └ Seconds
       │      │ │  └── Minutes
       │      │ └────── Hours (24h)
       │      └──────── Day
       └───────────────── Year Month
```

**Example:**
```
query_20240501_143025.md
       2024 05 01 14 30 25
       April 5, 2024 at 2:30:25 PM
```

---

## Troubleshooting

### Issue: "Can't connect to Ollama"

```
Error: Failed to connect to http://10.0.0.38:11434
```

**Reasons:**
- Ollama not running on Linux PC
- Wrong IP address
- Wrong port
- Network unreachable

**Solutions:**

1. Check Ollama running:
   ```bash
   ssh user@10.0.0.38
   ollama list
   ```

2. Verify IP:
   ```bash
   hostname -I
   ```

3. Update OLLAMA_URL:
   ```python
   OLLAMA_URL = "http://[correct_ip]:11434"
   ```

### Issue: "No data in database"

```
⚠️  No data in database! Run ingest first:
   python3 rag_ingest_recursive.py /path/to/code/
```

**Reasons:**
- Ingest script not run yet
- Wrong CHROMA_PATH
- Wrong COLLECTION name

**Solutions:**

1. Run ingest first:
   ```bash
   python3 rag_ingest_recursive.py ~/.arduino15/
   ```

2. Check database exists:
   ```bash
   ls -la ./chroma_db/
   ```

3. Verify CHROMA_PATH matches:
   ```python
   # In both scripts:
   CHROMA_PATH = "./chroma_db"  # Same!
   ```

### Issue: "Context window exceeded"

```
Error: the input length exceeds the context length (status code: 400)
```

**Reasons:**
- Too many queries in history
- TOP_K too high (too many chunks)
- Very long question

**Solutions:**

1. Clear history:
   ```
   /clear
   ```

2. Reduce TOP_K:
   ```python
   TOP_K = 3  # From 5
   ```

3. Reduce MAX_CONTEXT_WINDOW setting:
   ```python
   MAX_CONTEXT_WINDOW = 16384  # From 32768
   ```

### Issue: "Slow responses"

**Reasons:**
- Large model (7B parameters)
- Many chunks to retrieve (TOP_K=10)
- Network latency

**Solutions:**

1. Reduce TOP_K:
   ```python
   TOP_K = 3  # Fewer chunks = faster
   ```

2. Reduce NUM_PREDICT:
   ```python
   NUM_PREDICT = 256  # Shorter responses
   ```

3. Run on Linux (not Mac):
   - Eliminates network latency
   - Direct access to Ollama

### Issue: "Poor answer quality"

**Reasons:**
- Temperature too high
- TOP_K too low (not enough context)
- Wrong EMBED_MODEL
- Ingested wrong files

**Solutions:**

1. Lower temperature:
   ```python
   TEMPERATURE = 0.2  # More focused
   ```

2. Increase TOP_K:
   ```python
   TOP_K = 10  # More documents
   ```

3. Verify embedding model:
   ```python
   # Must match ingest script!
   EMBED_MODEL = "nomic-embed-text"
   ```

4. Re-ingest data:
   ```bash
   # Make sure right files ingested
   python3 rag_ingest_recursive.py ~/.arduino15/
   ```

---

## Summary

**What the script does:**
1. Loads vector database with ingested files
2. Takes user questions (single or multi-line)
3. Retrieves relevant document chunks
4. Sends to LLM with conversation context
5. Streams response token-by-token
6. Saves output to markdown file
7. Tracks conversation history
8. Shows context window usage

**Key concepts:**
- **RAG**: Retrieval-Augmented Generation
- **Chunks**: Document pieces from ingestion
- **Embeddings**: Vector representations
- **Context Window**: Token limit
- **Conversation Memory**: Previous Q&A
- **Streaming**: Real-time response

**Customization:**
- Change TEMPERATURE for precision
- Change TOP_K for more/fewer chunks
- Change MAX_CONTEXT_WINDOW for token limit
- Change NUM_PREDICT for response length
- Adjust TOP_P for creativity

**Best practices:**
- Run on Linux (faster)
- Use `/clear` between topics
- Monitor context % (stay < 85%)
- Review output files
- Adjust settings for your use case
