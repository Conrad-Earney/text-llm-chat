import re
import requests
import time

from config import (
    DUMMY_AI_REPLY,
    DUMMY_AI_REPLY_DELAY_SEC,
    DUMMY_AI_REPLY_ENABLED,
    OLLAMA_MODEL,
    OLLAMA_URL,
    REQUEST_TIMEOUT_SEC,
)


_BRACKETED_TEXT_RE = re.compile(r"\[[^\[\]]*\]")


def _participant_error(reason):
    return "ERROR: {}. Please let the experimenter know.".format(reason)


def strip_gesture_tags(text):
    text = _BRACKETED_TEXT_RE.sub("", str(text or ""))
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    return text.strip()


def generate_reply(messages):
    if DUMMY_AI_REPLY_ENABLED:
        if DUMMY_AI_REPLY_DELAY_SEC > 0:
            time.sleep(DUMMY_AI_REPLY_DELAY_SEC)
        return DUMMY_AI_REPLY

    if not messages:
        return _participant_error("No model request was created")

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
            timeout=REQUEST_TIMEOUT_SEC,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout:
        return _participant_error("The model request timed out")
    except requests.RequestException:
        return _participant_error("The model request failed")
    except ValueError:
        return _participant_error("The model returned an unreadable response")

    message = payload.get("message", {})
    reply = strip_gesture_tags(message.get("content", ""))
    if not isinstance(reply, str) or not reply.strip():
        return _participant_error("The model returned an empty response")

    return reply
