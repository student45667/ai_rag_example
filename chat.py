#!/usr/bin/env python3
"""
chat.py — Simple AI chatbot using Ollama + LlamaIndex
======================================================
- Talks to a local Ollama model over the network
- Remembers conversation history automatically
- Saves the full conversation to a .md file when you exit

Run:   python3 chat.py
Stop:  type  quit / exit / /bye  or press Ctrl+C
"""

import datetime
import sys

from llama_index.llms.ollama import Ollama
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import SimpleChatEngine


# ════════════════════════════════════════════════════════════════════════════
# SETTINGS  — change these to match your setup
# ════════════════════════════════════════════════════════════════════════════

# IP address and port of the machine running Ollama
OLLAMA_URL = "http://10.0.0.38:11434"

# Which model to use — must be already pulled in Ollama
MODEL = "qwen2.5-coder:7b"

# How the bot should behave — change this to suit your use case
SYSTEM_PROMPT = "You are a helpful coding assistant."

# Maximum conversation history in tokens.
# When the limit is reached, oldest messages are dropped automatically.
# 4500 is safe for an 8192 token context window.
HISTORY_BUFFER = 4500


# ════════════════════════════════════════════════════════════════════════════
# SESSION LOG  — one .md file per run, named with the current time
# ════════════════════════════════════════════════════════════════════════════

# Example filename:  session_20260425_143207.md
timestamp    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
SESSION_FILE = f"session_{timestamp}.md"


# ════════════════════════════════════════════════════════════════════════════
# CHAT ENGINE SETUP
# ════════════════════════════════════════════════════════════════════════════

# Connect to the Ollama model
llm = Ollama(
    model=MODEL,
    base_url=OLLAMA_URL,
    request_timeout=600     # wait up to 10 minutes for a response
)

# Memory buffer — keeps the last HISTORY_BUFFER tokens of conversation.
# Older messages are dropped automatically when the buffer is full.
memory = ChatMemoryBuffer.from_defaults(token_limit=HISTORY_BUFFER)

# The chat engine combines the LLM + memory into one simple interface.
# You just call chat_engine.chat("your message") and it handles the rest.
chat_engine = SimpleChatEngine.from_defaults(
    llm=llm,
    memory=memory,
    system_prompt=SYSTEM_PROMPT,
)


# ════════════════════════════════════════════════════════════════════════════
# SAVE CONVERSATION
# ════════════════════════════════════════════════════════════════════════════

def save_session():
    """
    Write the full conversation to a markdown file.
    Called automatically when the user exits.
    chat_engine.chat_history contains all messages in order.
    """
    msgs = chat_engine.chat_history

    if not msgs:
        print("Nothing to save.")
        return

    with open(SESSION_FILE, "w") as f:
        for msg in msgs:
            # label each message by who sent it
            label = "**You**" if msg.role == "user" else "**Bot**"
            f.write(f"{label}: {msg.content}\n\n---\n\n")

    print(f"\n💾 Conversation saved to: {SESSION_FILE}")


# ════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ════════════════════════════════════════════════════════════════════════════

def run():
    """
    Main conversation loop.
    Reads user input, sends it to the model, prints the reply.
    Exits cleanly on quit commands or Ctrl+C.
    """
    print(f"\n🤖 Chatbot ready  —  model: {MODEL}")
    print(f"📄 Session will be saved to: {SESSION_FILE}")
    print("Type  quit / exit / /bye  to stop.\n")
    print("-" * 50)

    try:
        while True:
            # get input from user
            user_input = input("You: ").strip()

            # skip empty lines
            if not user_input:
                continue

            # exit commands
            if user_input.lower() in ["quit", "exit", "goodbye", "/bye"]:
                print("Goodbye!")
                break

            # send message to model and print reply
            response = chat_engine.chat(user_input)
            print(f"\nBot: {response}\n")
            print("-" * 50)

    except KeyboardInterrupt:
        # user pressed Ctrl+C
        print("\nStopped.")

    finally:
        # always save on exit — whether normal or Ctrl+C
        save_session()


# ════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    run()
