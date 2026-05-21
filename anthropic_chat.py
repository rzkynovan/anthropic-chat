import json
import os
from datetime import datetime
from anthropic import Anthropic

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_memory.json")
SYSTEM_PROMPT = "Kamu adalah asisten AI yang helpful dan ramah. Kamu bisa mengingat seluruh percakapan sebelumnya dengan user."

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"conversations": {}}


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


def get_session_id():
    return datetime.now().strftime("%Y-%m-%d")


def chat(user_input, session_id=None):
    memory = load_memory()

    if session_id is None:
        session_id = get_session_id()

    if session_id not in memory["conversations"]:
        memory["conversations"][session_id] = []

    messages = memory["conversations"][session_id]
    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    assistant_text = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_text})

    save_memory(memory)

    return assistant_text


def list_sessions():
    memory = load_memory()
    return list(memory["conversations"].keys())


def clear_session(session_id=None):
    memory = load_memory()
    if session_id is None:
        session_id = get_session_id()
    if session_id in memory["conversations"]:
        del memory["conversations"][session_id]
        save_memory(memory)


def interactive():
    print("=" * 50)
    print("  Anthropic Chat with Memory")
    print("  Perintah: /quit, /clear, /sessions, /switch <id>")
    print("=" * 50)

    session_id = get_session_id()
    memory = load_memory()

    if session_id in memory["conversations"]:
        msg_count = len(memory["conversations"][session_id])
        print(f"\n[Session: {session_id} | {msg_count} pesan tersimpan]")

    while True:
        try:
            user_input = input("\nKamu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue

        if user_input == "/quit":
            print("Bye!")
            break

        if user_input == "/clear":
            clear_session(session_id)
            print(f"Session {session_id} dihapus.")
            continue

        if user_input == "/sessions":
            sessions = list_sessions()
            print(f"Sessions: {sessions if sessions else 'Kosong'}")
            continue

        if user_input.startswith("/switch "):
            session_id = user_input.split(" ", 1)[1]
            memory = load_memory()
            msg_count = len(memory["conversations"].get(session_id, []))
            print(f"[Session: {session_id} | {msg_count} pesan tersimpan]")
            continue

        try:
            response = chat(user_input, session_id)
            print(f"\nAI: {response}")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    interactive()