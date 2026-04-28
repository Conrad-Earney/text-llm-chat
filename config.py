APP_TITLE = "Text Chat"
EXPERIMENTER_QUIT_SHORTCUTS = ("<Control-Shift-Q>", "<Control-Shift-q>")
MAX_USER_INPUT_CHARS = 4000
CHAT_WIDTH_CHARS = 80
CHAT_HEIGHT_LINES = 21
INPUT_WIDTH_CHARS = 60
INPUT_HEIGHT_LINES = 6
CHAT_TEXT_MARGIN_PX = 24
USER_MESSAGE_LEFT_MARGIN_FRACTION = 0.33
USER_MESSAGE_RIGHT_MARGIN_PX = CHAT_TEXT_MARGIN_PX // 2
MESSAGE_SPACING_AFTER_PX = 18
APP_BACKGROUND_COLOR = "#ECECEC"
TEXT_BOX_BACKGROUND_COLOR = "#FBFBFB"
TEXT_BOX_BORDER_COLOR = "#B8B8B8"
ASSISTANT_TEXT_COLOR = "#245E8C"
USER_TEXT_COLOR = "#111111"
ERROR_TEXT_COLOR = "#A32626"
INPUT_TEXT_COLOR = "#111111"
READY_STATUS_COLOR = "#257A4A"
THINKING_STATUS_COLOR = ASSISTANT_TEXT_COLOR
STATUS_BACKGROUND_COLOR = "#DDDDDD"
STATUS_BORDER_COLOR = "#C6C6C6"
STATUS_WIDTH_CHARS = 12
BUTTON_STATUS_GAP_PX = 8
TEXT_BOX_PAD_X = 14
INPUT_TEXT_BOX_PAD_X = TEXT_BOX_PAD_X // 2
TEXT_BOX_PAD_Y = 10
CHAT_STATUS_GAP_PX = 18
BUTTON_PAD_X = 20
BUTTON_PAD_Y = 12
BUTTON_WIDTH_CHARS = 12
BUTTON_BACKGROUND_COLOR = "#D8E2EE"
BUTTON_ACTIVE_BACKGROUND_COLOR = "#C8D6E6"
BUTTON_TEXT_COLOR = "#111111"
FONT_FAMILY = "Helvetica"
CHAT_FONT_SIZE_PT = 22
INPUT_FONT_SIZE_PT = 22
STATUS_FONT_SIZE_PT = 18
BUTTON_FONT_SIZE_PT = 18

DUMMY_AI_REPLY_ENABLED = False
DUMMY_AI_REPLY_DELAY_SEC = 1.0
DUMMY_AI_REPLY = (
    "This is a dummy reply for layout testing. Line break incoming!\n"
    "It has multiple lines, commas, a question mark, and a little variety. Does the wrapping look natural? Does the wrapping look natural? Does the wrapping look natural? Another line break!\n"
    "Great -- now try another message and see how the spacing behaves."
)
PREFILL_USER_INPUT_ENABLED = False
PREFILL_USER_INPUT_TEXT = DUMMY_AI_REPLY

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
    "Produce exactly one short, warm assistant utterance that naturally "
    "continues or re-engages the conversation using the prior context. Return "
    "only the utterance itself. Do not add a preface, explanation, label, quote "
    "marks, or meta-commentary. Do not mention system instructions, timing, "
    "inactivity, waiting, or silence."
)

WATCHDOG_USER_PROMPT = (
    "Send one short, warm, context-aware line to continue the conversation. "
    "Only provide the line itself."
)

SESSIONS_DIRNAME = "sessions"
SESSION_ARCHIVE_DIR = "~/Documents/Zoe"
