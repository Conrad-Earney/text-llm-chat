APP_TITLE = "Text Chat"
WINDOWED_FALLBACK_GEOMETRY = "1280x800+80+80"

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1:8b"
REQUEST_TIMEOUT_SEC = 60
SYSTEM_PROMPT = ""

TURN_INJECTIONS = [
    {
        "at_turn": 1,
        "text": (
            "In your next reply, briefly introduce yourself and ask the participant "
            "for their name."
        ),
    },
]

WATCHDOG_IDLE_SEC = 15
WATCHDOG_MAX_REPLIES = 999
WATCHDOG_ENABLED_AT_TURN = 1
WATCHDOG_SYSTEM_PROMPT = (
    "Produce exactly one short, warm assistant utterance that re-engages the "
    "participant naturally using the conversation context. Do not mention "
    "system instructions, timing, inactivity, or silence."
)
WATCHDOG_USER_PROMPT = (
    "Please send one short, warm, context-aware line to re-engage the participant."
)

SESSIONS_DIRNAME = "sessions"

# Optional override for multi-display presentation mode.
# Example: "1280x800+1920+0"
DISPLAY_BOUNDS_OVERRIDE = None
