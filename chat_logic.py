import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"
REQUEST_TIMEOUT_SEC = 60


def generate_reply(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=REQUEST_TIMEOUT_SEC,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout:
        return "I'm sorry, but I took too long to reply. Please let the experimenter know."
    except requests.RequestException:
        return "I'm sorry, but I couldn't generate a reply just now. Please let the experimenter know."
    except ValueError:
        return "I'm sorry, but I returned an unreadable response. Please let the experimenter know."

    reply = payload.get("response", "")
    if not isinstance(reply, str) or not reply.strip():
        return "I'm sorry, but I couldn't generate a usable reply just now. Please let the experimenter know."

    return reply
