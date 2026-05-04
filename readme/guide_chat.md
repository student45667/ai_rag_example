# chat.py — Beginner's Code Guide

> A simple AI chatbot that talks to a local Ollama model, remembers
> the conversation, and saves it to a file when you exit.

---

## What this script does

```
You type a message
        ↓
chat.py sends it to Ollama (running on a local network machine)
        ↓
The model generates a reply — streamed token by token
        ↓
The reply is printed as it arrives
        ↓
On exit — the full conversation is saved to a .md file
```

---

## The imports

```python
import datetime   # used to create a timestamp for the session filename
import os         # used to create the output/ folder if it doesn't exist
import sys        # used for sys.exit() — clean program termination

from llama_index.llms.ollama import Ollama
# LlamaIndex wrapper around Ollama.
# Handles the HTTP connection to the Ollama server for us.
# Without this we'd have to write raw HTTP requests manually.

from llama_index.core.memory import ChatMemoryBuffer
# Manages conversation history automatically.
# Keeps the last N tokens of conversation.
# Drops oldest messages when the buffer is full — prevents overflow.

from llama_index.core.chat_engine import SimpleChatEngine
# The "engine" that combines LLM + memory into one object.
# You call chat_engine.chat("message") and it handles everything:
#   - sending history + new message to the model
#   - storing the reply in memory
#   - returning the response
```

---

## Settings

```python
OLLAMA_URL = "http://10.0.0.38:11434"
```
The IP address and port of the machine running Ollama.
- `10.0.0.38` — the machine on your local network where Ollama is installed
- `11434` — Ollama's default port
- Change to `http://localhost:11434` if Ollama runs on the same machine

```python
MODEL = "qwen2.5-coder:7b"
```
The name of the model to use. Must already be downloaded in Ollama (`ollama pull qwen2.5-coder:7b`).
- `7b` means 7 billion parameters — a medium-sized model
- Works well for code questions and general chat

```python
SYSTEM_PROMPT = "You are a helpful coding assistant."
```
This is the model's instruction — its "job description". It is sent as the first message in every conversation (as `role: system`). The model will follow this instruction throughout the session. Change it to anything: `"You are a Spanish teacher"`, `"You are a pirate"`, etc.

```python
HISTORY_BUFFER = 4500
```
How many tokens of conversation history to keep in memory.
- 1 token ≈ 0.75 words
- 4500 tokens ≈ ~3,375 words of conversation
- When full, the oldest messages are automatically dropped
- 4500 is safe because: `8192 (model limit) - 512 (system) - 512 (response) - ~2000 (question) = ~5168 free`

---

## Session file

```python
timestamp    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs("output", exist_ok=True)
SESSION_FILE = f"output/chat_session_{timestamp}.md"
```

**Line 1:** Gets the current date and time and formats it as `20260425_143207`
(year month day _ hour minute second).

**Line 2:** Creates the `output/` folder if it doesn't exist.
`exist_ok=True` means "don't crash if the folder already exists".

**Line 3:** Builds the full filename, e.g. `output/chat_session_20260425_143207.md`.
A new file is created every time you run the script — you never overwrite old sessions.

---

## Chat engine setup

```python
llm = Ollama(
    model=MODEL,
    base_url=OLLAMA_URL,
    request_timeout=600
)
```
Creates a connection object to the Ollama server.
`request_timeout=600` means wait up to 10 minutes for a response
— long responses or slow machines need this headroom.

```python
memory = ChatMemoryBuffer.from_defaults(token_limit=HISTORY_BUFFER)
```
Creates the memory buffer. Think of this as a sliding window:
```
[turn 1] [turn 2] [turn 3] ... [turn N]  ← window fits in HISTORY_BUFFER tokens
 oldest ──────────────────────────────── newest
 dropped when full                        always kept
```

```python
chat_engine = SimpleChatEngine.from_defaults(
    llm=llm,
    memory=memory,
    system_prompt=SYSTEM_PROMPT,
)
```
Combines everything into one object.
`from_defaults` is a LlamaIndex pattern meaning "create with sensible defaults,
only override what I specify". After this line you just call
`chat_engine.chat("your message")` and everything else is handled.

---

## save_session()

```python
def save_session():
    msgs = chat_engine.chat_history
```
`chat_history` is a list of all messages stored inside the chat engine.
Each item has `.role` (either `"user"` or `"assistant"`) and `.content` (the text).

```python
    if not msgs:
        print("Nothing to save.")
        return
```
Guard against empty sessions — if you open and immediately quit, nothing is saved.

```python
    with open(SESSION_FILE, "w") as f:
        for msg in msgs:
            label = "**You**" if msg.role == "user" else "**Bot**"
            f.write(f"{label}: {msg.content}\n\n---\n\n")
```
`with open(..., "w")` — opens file for writing. "w" overwrites if exists.
`msg.role == "user"` — checks who sent the message.
`**You**` — bold markdown formatting for readability.
`\n\n---\n\n` — markdown horizontal rule between messages.

The resulting file looks like:
```markdown
**You**: What is a pointer in C?

---

**Bot**: A pointer is a variable that stores a memory address...

---
```

---

## run() — the main loop

```python
print(f"\n🤖 Chatbot ready  —  model: {MODEL}")
print(f"📄 Session will be saved to: {SESSION_FILE}")
```
Tells the user what model is running and where the session will be saved —
useful before a long session so you know where to find it later.

### Multi-line input

```python
print("You (type . to send):")
lines = []
while True:
    line = input()
    if line.strip() == ".":
        break
    if line.strip().lower() in ["quit", "exit", "goodbye", "/bye"]:
        lines = [line.strip()]   # pass to exit check below
        break
    lines.append(line)
user_input = "\n".join(lines).strip()
```

Why multi-line? So you can paste code or long text without it sending immediately.

**How it works:**
1. `lines = []` — start with an empty list
2. `input()` — read one line at a time
3. If the line is `.` alone — stop collecting, send what we have
4. If the line is an exit command — store it and break (will be caught below)
5. Otherwise — add the line to the list
6. `"\n".join(lines)` — join all lines back into one string with newlines between them

```
You type:           lines list becomes:
  Hello             ["Hello"]
  this is           ["Hello", "this is"]
  my question       ["Hello", "this is", "my question"]
  .                 ← stop
  
user_input = "Hello\nthis is\nmy question"
```

### Streaming response

```python
response = chat_engine.stream_chat(user_input)
print("\nBot: ", end="", flush=True)
for token in response.response_gen:
    print(token, end="", flush=True)
print("\n")
```

`stream_chat` vs `chat`:
- `chat(msg)` — waits for the complete response before returning. Feels slow.
- `stream_chat(msg)` — returns immediately, gives you tokens one by one as generated.

`end=""` — don't print a newline after each token (they all print on the same line).
`flush=True` — force each token to appear on screen immediately (not buffered).
`response.response_gen` — a generator that yields tokens one by one.

### try / except / finally

```python
try:
    while True:
        ...          # normal loop
except KeyboardInterrupt:
    print("\nStopped.")   # user pressed Ctrl+C
finally:
    save_session()        # ALWAYS runs — even on Ctrl+C
```

`finally` is the key here — it guarantees `save_session()` is called whether
the user types `/bye` or hits Ctrl+C. The conversation is never lost.

---

## Entry point

```python
if __name__ == "__main__":
    run()
```
Standard Python pattern. This block only runs when you execute the file directly:
```bash
python3 chat.py    ← runs run()
```
It does NOT run if another script imports this file as a module.

---

## Summary — data flow

```
chat.py starts
      ↓
llm + memory + system_prompt → chat_engine created
      ↓
while True:
  collect lines until "."
      ↓
  chat_engine.stream_chat(user_input)
      ↓
  [internally: system + memory history + user_input → Ollama → reply]
      ↓
  stream reply token by token to screen
      ↓
  reply stored in memory automatically
      ↓
user types /bye or Ctrl+C
      ↓
save_session() writes chat_history to output/chat_session_TIMESTAMP.md
```

---

*Guide written April 2026*
