import requests

from config import OLLAMA_MODEL, OLLAMA_URL, REQUEST_TIMEOUT_SEC


def generate_reply(messages):
    if not messages:
        return "I'm sorry, but I couldn't generate a reply just now. Please let the experimenter know."

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
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

    message = payload.get("message", {})
    reply = message.get("content", "")
    if not isinstance(reply, str) or not reply.strip():
        return "I'm sorry, but I couldn't generate a usable reply just now. Please let the experimenter know."

    return reply
