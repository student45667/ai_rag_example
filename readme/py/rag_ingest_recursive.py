#!/usr/bin/env python3
"""
Recursive RAG Ingestion for Code & Text Files
==============================================

Automatically processes ALL files in nested folders:
- arduino15/packages/esp32/
  ├─ hardware/
  │  ├─ esp32/
  │  │  ├─ cores/
  │  │  ├─ libraries/
  │  │  └─ variants/
  └─ tools/

Usage:
    python3 rag_ingest_recursive.py arduino15/packages/esp32/
    python3 rag_ingest_recursive.py ~/.arduino15/
"""

import os
import sys
from pathlib import Path
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

OLLAMA_URL = "http://10.0.0.38:11434"
LLM_MODEL = "qwen2.5-coder:7b"
#LLM_MODEL = "qwen3.5:latest"
EMBED_MODEL = "nomic-embed-text"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "code_files"

# File types to process
SUPPORTED_TYPES = (
    ".c", ".h", ".cpp", ".ino",      # Code files
    ".md", ".txt",                    # Documentation
    ".py", ".js", ".java",            # Additional languages
    ".xml", ".json",                  # Config files
)

# Folders to skip (optional)
SKIP_FOLDERS = {
    '.git', '__pycache__', 'node_modules', 
    '.venv', 'venv', '.DS_Store'
}


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

Settings.chunk_size = 512
Settings.chunk_overlap = 64

print("✓ LLM and embeddings configured")


# ════════════════════════════════════════════════════════════════════════════
# SETUP VECTOR DATABASE
# ════════════════════════════════════════════════════════════════════════════

print(f"📦 Setting up vector database at: {CHROMA_PATH}")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

print(f"✓ Vector database ready")


# ════════════════════════════════════════════════════════════════════════════
# RECURSIVE FILE FINDER
# ════════════════════════════════════════════════════════════════════════════

def find_all_files(directory, supported_types, skip_folders):
    """
    Recursively find all supported files in directory and subdirectories
    
    Args:
        directory: Root directory to search
        supported_types: Tuple of file extensions to process
        skip_folders: Set of folder names to skip
    
    Returns:
        List of file paths
    """
    found_files = []
    
    for root, dirs, files in os.walk(directory):
        # Remove skip folders from dirs (prevents os.walk from descending)
        dirs[:] = [d for d in dirs if d not in skip_folders]
        
        # Find matching files in this directory
        for filename in files:
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in supported_types:
                file_path = os.path.join(root, filename)
                found_files.append(file_path)
    
    return sorted(found_files)


# ════════════════════════════════════════════════════════════════════════════
# INGEST FILE
# ════════════════════════════════════════════════════════════════════════════

def ingest_file(file_path):
    """
    Read a code/text file and store it in the vector database
    """
    
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(file_path)[1]
    
    # Get relative path for better context
    rel_path = os.path.relpath(file_path)
    
    print(f"   📄 {rel_path}")
    print(f"      Size: {file_size:,} bytes")
    
    try:
        # Read file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        
        # Skip empty files
        if not text.strip():
            print(f"      ⏭️  Empty file, skipping")
            return False
        
        print(f"      Content: {len(text):,} characters")
        
        # Create document with rich metadata
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
        
        # Store in vector database
        print(f"      ⏳ Storing...")
        VectorStoreIndex.from_documents(
            [document],
            storage_context=storage_context,
            show_progress=False
        )
        
        print(f"      ✅ Stored!")
        return True
    
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    """
    Main entry point: recursively ingest all supported files
    """
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 rag_ingest_recursive.py <folder>")
        print("\nExamples:")
        print("  python3 rag_ingest_recursive.py ~/.arduino15/packages/esp32/")
        print("  python3 rag_ingest_recursive.py ./my_project/")
        print(f"\nSupported types: {', '.join(SUPPORTED_TYPES)}")
        sys.exit(1)
    
    target = sys.argv[1]
    
    # Expand ~ if present
    target = os.path.expanduser(target)
    
    if not os.path.isdir(target):
        print(f"❌ Not a directory: {target}")
        sys.exit(1)
    
    print(f"📁 Scanning: {target}")
    print(f"   (recursively searching all subfolders)")
    print("-" * 70)
    
    # Find all files recursively
    files = find_all_files(target, SUPPORTED_TYPES, SKIP_FOLDERS)
    
    if not files:
        print(f"❌ No supported files found in {target}")
        print(f"Supported types: {', '.join(SUPPORTED_TYPES)}")
        sys.exit(1)
    
    print(f"\n📊 Found {len(files)} file(s) to process:\n")
    
    # Ingest files
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(files, 1):
        print(f"[{i}/{len(files)}]")
        if ingest_file(file_path):
            successful += 1
        else:
            failed += 1
        print()
    
    # Summary
    total_chunks = chroma_collection.count()
    print("=" * 70)
    print(f"✅ DONE!")
    print(f"   Files processed:  {successful}")
    print(f"   Files failed:     {failed}")
    print(f"   Total chunks:     {total_chunks}")
    print(f"   Database:         {CHROMA_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()
