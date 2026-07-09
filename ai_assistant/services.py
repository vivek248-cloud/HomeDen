import requests
import json
import time

from .prompts import SYSTEM_PROMPT

OLLAMA_URL = "http://31.97.62.126:11434/api/chat"
MODEL = "gemma3:1b"


def ask_ai(chat_history, user_message):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Add previous conversation
    messages.extend(chat_history)

    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "num_predict": 120
        }
    }

    print("=" * 80)
    print("Sending payload to Ollama")
    print(json.dumps(payload, indent=2))
    print("=" * 80)
    print("Payload size:", len(json.dumps(payload)))

    start = time.time()

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    elapsed = time.time() - start

    print(f"AI Response Time: {elapsed:.2f} seconds")

    response.raise_for_status()

    data = response.json()

    print("=" * 80)
    print("Ollama Response:")
    print(json.dumps(data, indent=2))
    print("=" * 80)

    return data["message"]["content"].strip()