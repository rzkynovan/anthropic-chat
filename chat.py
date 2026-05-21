import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_memory.json")
chat_history = []

def _load():
    global chat_history
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            chat_history = json.load(f)

def _save():
    with open(MEMORY_FILE, "w") as f:
        json.dump(chat_history, f, indent=2, ensure_ascii=False)

def ask(text):
    chat_history.append({"role": "user", "content": text})
    r = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="Kamu asisten AI yang ramah dan mengingat seluruh percakapan.",
        messages=chat_history,
    )
    reply = r.content[0].text
    chat_history.append({"role": "assistant", "content": reply})
    _save()
    return reply

def clear():
    global chat_history
    chat_history = []
    _save()

_load()