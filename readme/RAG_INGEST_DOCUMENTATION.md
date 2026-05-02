# RAG Ingest Recursive - Complete Documentation

## Overview

`rag_ingest_recursive.py` is a **file ingestion script** that automatically discovers all code and text files in nested folders, converts them to vector embeddings, and stores them in a vector database (ChromaDB) for later semantic search.

Think of it as:
- **Scanner**: Walks through all subdirectories
- **Reader**: Opens and reads code/text files
- **Converter**: Transforms text into numerical vectors (embeddings)
- **Storage**: Saves vectors + original text in database for fast retrieval

---

## Table of Contents

1. [Configuration Section](#configuration-section)
2. [Setup Phase](#setup-phase)
3. [File Discovery Function](#file-discovery-function)
4. [File Ingestion Function](#file-ingestion-function)
5. [Main Execution](#main-execution)
6. [How to Run](#how-to-run)
7. [What Gets Stored](#what-gets-stored)
8. [Understanding Chunks](#understanding-chunks)
9. [Troubleshooting](#troubleshooting)

---

## Configuration Section

### Location
Lines 26-47 at the top of the script

### OLLAMA_URL
```python
OLLAMA_URL = "http://10.0.0.38:11434"
```

**What it does:**
- Tells the script where Ollama is running
- IP address: `10.0.0.38` (your Linux PC)
- Port: `11434` (Ollama's default port)

**Change it if:**
- Ollama runs on different machine
- You want to use different port
- Example: `http://192.168.1.100:11434`

### LLM_MODEL
```python
LLM_MODEL = "qwen2.5-coder:7b"
```

**What it does:**
- Specifies which language model to use
- Only used for generating embeddings (not used during ingestion)
- Must match a model you have installed in Ollama

**Valid options:**
- `qwen2.5-coder:7b` (code-focused, your choice)
- `qwen3.5:latest` (general purpose)
- `mistral:7b-instruct` (general purpose)

### EMBED_MODEL
```python
EMBED_MODEL = "nomic-embed-text"
```

**What it does:**
- Specifies the embedding model (converts text to vectors)
- Different from LLM_MODEL - this one creates the numerical vectors
- Runs on Ollama to generate embeddings

**Why separate?**
- LLM: Understands meaning (for queries)
- EMBED_MODEL: Converts text to numbers (for storage)

### CHROMA_PATH
```python
CHROMA_PATH = "./chroma_db"
```

**What it does:**
- Directory where vector database is stored
- Relative path: `./chroma_db` = current folder
- Creates folder if doesn't exist

**Explanation:**
```
Your project folder/
├─ rag_ingest_recursive.py
├─ rag_query.py
└─ chroma_db/              ← Vector database stored here
   ├─ data/
   ├─ index/
   └─ metadata/
```

### COLLECTION_NAME
```python
COLLECTION_NAME = "code_files"
```

**What it does:**
- Names the collection inside ChromaDB
- Like a "table" in a database
- You can have multiple collections in same database

**Why it matters:**
```python
# In rag_query.py, it retrieves from same collection:
chroma_collection = chroma_client.get_or_create_collection("code_files")
```

### SUPPORTED_TYPES
```python
SUPPORTED_TYPES = (
    ".c", ".h", ".cpp", ".ino",      # Code files
    ".md", ".txt",                    # Documentation
    ".py", ".js", ".java",            # Additional languages
    ".xml", ".json",                  # Config files
)
```

**What it does:**
- Tuple of file extensions to process
- Only files with these extensions will be ingested
- Others are ignored (e.g., `.jpg`, `.pdf` skip)

**To add more file types:**
```python
SUPPORTED_TYPES = (
    ".c", ".h", ".cpp", ".ino",
    ".md", ".txt",
    ".py", ".js", ".java",
    ".xml", ".json",
    ".rs",                             # Add Rust files
    ".go",                             # Add Go files
)
```

### SKIP_FOLDERS
```python
SKIP_FOLDERS = {
    '.git', '__pycache__', 'node_modules', 
    '.venv', 'venv', '.DS_Store'
}
```

**What it does:**
- Set of folder names to skip during recursive search
- Prevents scanning unnecessary/large folders
- Speeds up ingestion

**Why these folders?**
- `.git`: Version control (10,000+ files)
- `__pycache__`: Python cache (compiled code, not source)
- `node_modules`: NPM packages (huge!)
- `.venv`, `venv`: Virtual environments (duplicate Python)
- `.DS_Store`: macOS system file (junk)

**To skip more folders:**
```python
SKIP_FOLDERS = {
    '.git', '__pycache__', 'node_modules', 
    '.venv', 'venv', '.DS_Store',
    'build',                           # Add build folder
    'dist',                            # Add distribution folder
    '.pytest_cache',                   # Add pytest cache
}
```

---

## Setup Phase

### What Happens First

Before any files are ingested, the script initializes three things:

#### 1. Setup LLM and Embeddings (Lines 56-75)

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

Settings.chunk_size = 512
Settings.chunk_overlap = 64
```

**Breaking it down:**

**`Settings.llm = Ollama(...)`**
- Creates connection to Ollama LLM
- `model=LLM_MODEL`: Which model to use
- `base_url=OLLAMA_URL`: Where Ollama is running
- `request_timeout=600`: Wait max 600 seconds for response

**`Settings.embed_model = OllamaEmbedding(...)`**
- Creates connection for embedding model
- This converts text → vectors (numbers)
- Used by ChromaDB to store searchable vectors

**`Settings.chunk_size = 512`**
- Splits large files into 512-token chunks
- Why? Model has token limits
- Example: 5,000 character file → split into chunks

**`Settings.chunk_overlap = 64`**
- Chunks overlap by 64 tokens
- Why? So no context is lost between chunks
- Example:
  ```
  Chunk 1: tokens 1-512
  Chunk 2: tokens 449-960 (overlap = 64)
  Chunk 3: tokens 897-1408
  ```

#### 2. Setup Vector Database (Lines 83-92)

```python
print(f"📦 Setting up vector database at: {CHROMA_PATH}")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
```

**What each line does:**

**`chromadb.PersistentClient(path=CHROMA_PATH)`**
- Creates persistent database at `./chroma_db/`
- "Persistent" = survives after script ends
- Next run: reuses same database

**`get_or_create_collection(COLLECTION_NAME)`**
- Creates "code_files" collection if doesn't exist
- Reuses existing collection if it does
- Like creating a table in a database

**`ChromaVectorStore(chroma_collection=chroma_collection)`**
- Wraps ChromaDB collection for LlamaIndex
- Handles vector storage format
- LlamaIndex needs this wrapper

**`StorageContext.from_defaults(vector_store=vector_store)`**
- Creates context for storing documents
- Tells LlamaIndex where to save vectors
- Used when creating VectorStoreIndex

---

## File Discovery Function

### Location
Lines 100-127

### Function Signature
```python
def find_all_files(directory, supported_types, skip_folders):
```

### Parameters

**`directory`** (str)
- Root folder to start searching
- Example: `/home/user/.arduino15/packages/esp32/`
- Can be absolute or relative path

**`supported_types`** (tuple)
- File extensions to include
- Example: `(".c", ".h", ".cpp", ".ino")`

**`skip_folders`** (set)
- Folder names to skip
- Example: `{'.git', '__pycache__', 'node_modules'}`

### How It Works: os.walk()

```python
for root, dirs, files in os.walk(directory):
    # root: current folder path
    # dirs: subfolders in current folder
    # files: files in current folder
```

**Example walk through folder:**
```
Start: /home/user/project/

Iteration 1:
  root = /home/user/project/
  dirs = ['src', 'tests', '.git']
  files = ['README.md', 'setup.py']

Iteration 2:
  root = /home/user/project/src/
  dirs = ['utils', 'core']
  files = ['main.py', 'config.py']

Iteration 3:
  root = /home/user/project/src/utils/
  dirs = []
  files = ['helper.py', 'constants.py']
```

### Filtering Folders

```python
dirs[:] = [d for d in dirs if d not in skip_folders]
```

**What it does:**
- Removes skip folders from `dirs` list
- `dirs[:] =` modifies list in-place (affects os.walk!)
- Prevents os.walk from descending into skipped folders

**Why important?**
```python
# WITHOUT filtering:
os.walk() processes .git/ (50,000 files!)

# WITH filtering:
os.walk() skips .git/ (saves time!)
```

### Checking File Extensions

```python
file_ext = os.path.splitext(filename)[1].lower()
if file_ext in supported_types:
    file_path = os.path.join(root, filename)
    found_files.append(file_path)
```

**Breaking it down:**

**`os.path.splitext(filename)[1]`**
- Splits `"driver.c"` into `("driver", ".c")`
- `[1]` gets the second part: `".c"`
- Example:
  ```python
  os.path.splitext("config.json") → ("config", ".json")
  os.path.splitext("readme.txt") → ("readme", ".txt")
  ```

**`.lower()`**
- Converts to lowercase
- So `".C"` matches `".c"`
- Handles case-insensitive filesystems

**`if file_ext in supported_types`**
- Check if extension is in our list
- Example: Is `".c"` in `(".c", ".h", ".cpp")`?

**`os.path.join(root, filename)`**
- Combines path properly for OS
- Handles Windows/Linux differences
- Example: `"/home/user"` + `"file.c"` → `"/home/user/file.c"`

### Return Value

```python
return sorted(found_files)
```

**What it returns:**
- List of absolute file paths
- Sorted alphabetically
- Example:
  ```python
  [
    '/home/user/project/src/core.c',
    '/home/user/project/src/driver.c',
    '/home/user/project/src/main.c',
  ]
  ```

---

## File Ingestion Function

### Location
Lines 134-195

### Function Signature
```python
def ingest_file(file_path):
```

### Parameters
**`file_path`** (str)
- Absolute path to file to ingest
- Example: `/home/user/project/driver.c`

### Step 1: Extract File Info

```python
file_name = os.path.basename(file_path)
file_size = os.path.getsize(file_path)
file_ext = os.path.splitext(file_path)[1]
rel_path = os.path.relpath(file_path)
```

**`os.path.basename(file_path)`**
- Gets just filename
- `/home/user/driver.c` → `driver.c`

**`os.path.getsize(file_path)`**
- Returns file size in bytes
- Example: `2345` bytes
- Used for logging

**`os.path.splitext(file_path)[1]`**
- Gets file extension
- `/home/user/driver.c` → `.c`
- Used to determine file type

**`os.path.relpath(file_path)`**
- Gets relative path from current directory
- Easier to read in logs
- Example: `src/driver.c` instead of `/home/user/project/src/driver.c`

### Step 2: Read File Content

```python
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

if not text.strip():
    print(f"      ⏭️  Empty file, skipping")
    return False
```

**`open(file_path, "r", ...)`**
- Opens file for reading
- `"r"` = read mode (not write)

**`encoding="utf-8"`**
- Reads as UTF-8 text
- Handles special characters
- Unicode support

**`errors="ignore"`**
- Ignores encoding errors
- Won't crash on corrupted files
- Continues reading

**`text.strip()`**
- Removes whitespace
- Checks if file is empty
- Skip empty files (no content to index)

### Step 3: Create Document Object

```python
document = Document(
    text=text,
    metadata={
        "filename": file_name,
        "source": file_path,
        "rel_path": rel_path,
        "type": "code" if file_ext in [".c", ".h", ".cpp", ".ino", ".py", ".js"] else "text",
        "file_size": file_size,
        "file_ext": file_ext,
    }
)
```

**`Document(text=text, metadata={...})`**
- Creates LlamaIndex Document object
- `text`: The actual file content
- `metadata`: Information ABOUT the file

**Metadata Breakdown:**
- `filename`: Just the filename (`driver.c`)
- `source`: Full path (for reference)
- `rel_path`: Relative path (readable)
- `type`: `"code"` or `"text"` (for filtering)
- `file_size`: Size in bytes (for statistics)
- `file_ext`: Extension (for identification)

**Why metadata?**
- Stored with vectors in database
- Retrieved when document is found
- Example:
  ```python
  # Later, when querying:
  found_doc = {
    "text": "void init() { ... }",
    "metadata": {
      "filename": "driver.c",
      "source": "/home/user/driver.c",
      ...
    }
  }
  ```

### Step 4: Store in Vector Database

```python
VectorStoreIndex.from_documents(
    [document],
    storage_context=storage_context,
    show_progress=False
)
```

**`VectorStoreIndex.from_documents()`**
- Main function that:
  1. Splits document into chunks (512 tokens)
  2. Generates embeddings for each chunk
  3. Stores in ChromaDB
  4. Creates searchable index

**`[document]`**
- List containing one document
- Could be multiple: `[doc1, doc2, doc3]`

**`storage_context=storage_context`**
- Where to store vectors
- Configured in setup phase

**`show_progress=False`**
- Don't show progress bar
- Keeps output clean

### Return Value

```python
return True  # or False on error
```

**Returns:**
- `True` if ingestion successful
- `False` if error occurred
- Used in main() to count success/failure

---

## Main Execution

### Location
Lines 202-265

### Function Signature
```python
def main():
```

### Phase 1: Validate Arguments

```python
if len(sys.argv) < 2:
    print("Usage:")
    print("  python3 rag_ingest_recursive.py <folder>")
    print("\nExamples:")
    print("  python3 rag_ingest_recursive.py ~/.arduino15/packages/esp32/")
    print("  python3 rag_ingest_recursive.py ./my_project/")
    print(f"\nSupported types: {', '.join(SUPPORTED_TYPES)}")
    sys.exit(1)
```

**What it does:**
- Checks if user provided a folder argument
- `sys.argv[0]`: Script name (`rag_ingest_recursive.py`)
- `sys.argv[1]`: First argument (folder path)
- If missing: shows usage and exits

**Example runs:**
```bash
python3 rag_ingest_recursive.py                    # ❌ Error: no folder
python3 rag_ingest_recursive.py ~/.arduino15/      # ✅ OK: folder provided
```

### Phase 2: Expand and Validate Path

```python
target = sys.argv[1]
target = os.path.expanduser(target)

if not os.path.isdir(target):
    print(f"❌ Not a directory: {target}")
    sys.exit(1)
```

**`os.path.expanduser(target)`**
- Expands `~` to home directory
- `~/.arduino15/` → `/home/user/.arduino15/`
- Only works if `~` is present

**`os.path.isdir(target)`**
- Checks if path is a directory
- Returns False if doesn't exist or is a file
- Validates before proceeding

### Phase 3: Find All Files

```python
files = find_all_files(target, SUPPORTED_TYPES, SKIP_FOLDERS)

if not files:
    print(f"❌ No supported files found in {target}")
    print(f"Supported types: {', '.join(SUPPORTED_TYPES)}")
    sys.exit(1)
```

**What it does:**
- Calls `find_all_files()` function
- Gets sorted list of all matching files
- Validates that files were found

### Phase 4: Ingest Each File

```python
successful = 0
failed = 0

for i, file_path in enumerate(files, 1):
    print(f"[{i}/{len(files)}]")
    if ingest_file(file_path):
        successful += 1
    else:
        failed += 1
    print()
```

**Breaking it down:**

**`enumerate(files, 1)`**
- Loops through files with counter starting at 1
- `i`: Counter (1, 2, 3, ...)
- `file_path`: Current file

**`print(f"[{i}/{len(files)}]")`**
- Shows progress: `[1/50]`, `[2/50]`, etc.
- Tells user which file being processed

**Counter logic:**
```python
if ingest_file(file_path):
    successful += 1        # Increment success
else:
    failed += 1            # Increment failure
```

### Phase 5: Summary

```python
total_chunks = chroma_collection.count()
print("=" * 70)
print(f"✅ DONE!")
print(f"   Files processed:  {successful}")
print(f"   Files failed:     {failed}")
print(f"   Total chunks:     {total_chunks}")
print(f"   Database:         {CHROMA_PATH}")
print("=" * 70)
```

**What's shown:**
- Success count
- Failure count
- Total chunks stored (how many document pieces)
- Database location

**Example output:**
```
======================================================================
✅ DONE!
   Files processed:  23
   Files failed:     2
   Total chunks:     156
   Database:         ./chroma_db
======================================================================
```

---

## How to Run

### Basic Usage

```bash
# From project folder where script is
python3 rag_ingest_recursive.py ~/.arduino15/packages/esp32/
```

### What Happens

1. **Startup messages** (1-2 seconds)
   ```
   ⚙️  Setting up LLM and embeddings...
   ✓ LLM and embeddings configured
   📦 Setting up vector database at: ./chroma_db
   ✓ Vector database ready
   ```

2. **File discovery** (depends on folder size)
   ```
   📁 Scanning: /home/user/.arduino15/packages/esp32/
      (recursively searching all subfolders)
   ```

3. **Processing** (1-2 minutes per 100 files)
   ```
   📊 Found 50 file(s) to process:
   
   [1/50]
      📄 hardware/esp32/cores/main.cpp
      Size: 5,234 bytes
      Content: 5,234 characters
      ⏳ Storing...
      ✅ Stored!
   
   [2/50]
      📄 hardware/esp32/variants/pins.h
      ...
   ```

4. **Summary** (instant)
   ```
   ✅ DONE!
      Files processed:  50
      Files failed:     0
      Total chunks:     342
      Database:         ./chroma_db
   ```

### Common Commands

**Ingest Arduino files:**
```bash
python3 rag_ingest_recursive.py ~/.arduino15/packages/esp32/
```

**Ingest your project:**
```bash
python3 rag_ingest_recursive.py ./my_project/
```

**Ingest current folder:**
```bash
python3 rag_ingest_recursive.py .
```

---

## What Gets Stored

### In ChromaDB Database

For each file chunk, the following is stored:

```python
{
  "id": "chunk_001_driver_c",
  "embedding": [0.234, 0.456, 0.789, ...],  # Vector (384 dimensions)
  "document": "void init() {\n  i2c_init();\n}",
  "metadata": {
    "filename": "driver.c",
    "source": "/home/user/driver.c",
    "rel_path": "src/driver.c",
    "type": "code",
    "file_size": 2345,
    "file_ext": ".c"
  }
}
```

### On Disk

```
./chroma_db/
├─ chroma.db          # Main database
├─ data/              # Vector data
│  └─ ...
├─ index/             # Search index
│  └─ ...
└─ metadata/          # Metadata store
   └─ ...
```

---

## Understanding Chunks

### Why Chunk?

Models have token limits. Example:
- File size: 50,000 characters
- Token count: ~12,500 tokens
- Model context: 4,096 tokens max
- **Solution**: Split into chunks

### How Chunking Works

```
Original text: 12,500 tokens

Settings:
- chunk_size = 512
- chunk_overlap = 64

Result:
┌─────────────────────────────────────────────────┐
│ Chunk 1: tokens 1-512                           │
└─────────────────────────────────────────────────┘
                 ↓ overlap
                ┌──────────────────────────────────────────────┐
                │ Chunk 2: tokens 449-960 (64 token overlap)   │
                └──────────────────────────────────────────────┘
                                   ↓ overlap
                                  ┌──────────────────────────────────┐
                                  │ Chunk 3: tokens 897-1408        │
                                  └──────────────────────────────────┘
```

### Overlap Purpose

Without overlap:
```
Chunk 1: "void init() {"
Chunk 2: "  delay(100);"  ← Lost context of init()!
```

With overlap (64 tokens):
```
Chunk 1: "void init() { ... code before ..."
Chunk 2: "... code before ... delay(100); ... code after ..."
         ↑ Has context of init()!
```

---

## Troubleshooting

### Issue: "❌ Not a directory"

```
python3 rag_ingest_recursive.py /wrong/path/
```

**Solution:**
- Check path is correct
- Use `ls -la /your/path/` to verify
- Use absolute paths: `~/.arduino15/` not `arduino15/`

### Issue: "❌ No supported files found"

```
python3 rag_ingest_recursive.py /wrong/type/folder/
```

**Reasons:**
- Folder has no code files
- Files have wrong extensions
- All files are in SKIP_FOLDERS

**Solution:**
- Check folder contains supported types
- Add more file types to SUPPORTED_TYPES
- Remove from SKIP_FOLDERS if needed

### Issue: Files take long time to ingest

**Reasons:**
- Large files (>1MB each)
- Many files (>1000)
- Slow embedding model
- Network latency to Ollama

**Solutions:**
```python
# Increase chunk size (fewer chunks to embed)
Settings.chunk_size = 1024

# Skip more folders
SKIP_FOLDERS = {..., 'build', 'dist', 'node_modules'}

# Reduce supported types
SUPPORTED_TYPES = (".c", ".h", ".cpp")
```

### Issue: "Connection refused" error

```
Error: Failed to connect to http://10.0.0.38:11434
```

**Reasons:**
- Ollama not running on Linux PC
- Wrong IP address
- Wrong port

**Solutions:**
1. Check Ollama is running:
   ```bash
   ssh user@10.0.0.38
   ollama serve
   ```

2. Check correct IP:
   ```bash
   ssh user@10.0.0.38
   hostname -I
   ```

3. Update OLLAMA_URL:
   ```python
   OLLAMA_URL = "http://[correct_ip]:11434"
   ```

### Issue: "Out of memory" error

**Reason:**
- Processing too many large files at once

**Solutions:**
1. Process in batches:
   ```bash
   # First batch
   python3 rag_ingest_recursive.py ~/code/part1/
   
   # Second batch
   python3 rag_ingest_recursive.py ~/code/part2/
   ```

2. Reduce chunk size:
   ```python
   Settings.chunk_size = 256  # Smaller chunks
   ```

---

## Summary

**What the script does:**
1. Scans folder recursively
2. Finds all code/text files
3. Reads file contents
4. Splits into chunks
5. Converts to embeddings
6. Stores in vector database

**Key concepts:**
- **Chunks**: Split files into manageable pieces
- **Embeddings**: Convert text to vectors
- **Vector Database**: Store vectors for fast search
- **Metadata**: Store file info with vectors

**Output:**
- `./chroma_db/` folder with vector database
- Ready for RAG queries
