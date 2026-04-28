# text-llm-chat

Small Tkinter chat app for running a local text model through Ollama and logging each session.

## What It Does

- Shows a simple participant-facing chat window
- Sends conversation history to a local Ollama chat model
- Builds each Ollama request from explicit conversation state, system prompts, and turn injections
- Disables interaction while the model is generating a reply
- Can send watchdog re-engagement replies after periods of participant inactivity
- Logs each turn to a timestamped session directory

## Requirements

- Python 3
- `requests`
- Ollama running locally
- The configured Ollama model installed locally

## Setup

Install the Python dependency:

```bash
python3 -m pip install requests
```

Make sure Ollama is running, then pull the default model if needed:

```bash
ollama pull llama3.1:8b
```

## Run

```bash
python3 gui.py
```

## Configuration

Configuration lives in `config.py`.

Conversation state and Ollama message construction live in `conversation.py`.

Main settings are grouped by purpose:

- App/session: `APP_TITLE`, `EXPERIMENTER_QUIT_SHORTCUTS`, `SESSIONS_DIRNAME`
- Input limits: `MAX_USER_INPUT_CHARS`
- Layout: `CHAT_WIDTH_CHARS`, `CHAT_HEIGHT_LINES`, `INPUT_WIDTH_CHARS`, `INPUT_HEIGHT_LINES`, `CHAT_STATUS_GAP_PX`, `BUTTON_STATUS_GAP_PX`
- Message spacing: `CHAT_TEXT_MARGIN_PX`, `USER_MESSAGE_LEFT_MARGIN_FRACTION`, `USER_MESSAGE_RIGHT_MARGIN_PX`, `MESSAGE_SPACING_AFTER_PX`
- Colors: `APP_BACKGROUND_COLOR`, `TEXT_BOX_BACKGROUND_COLOR`, `TEXT_BOX_BORDER_COLOR`, `ASSISTANT_TEXT_COLOR`, `USER_TEXT_COLOR`, `ERROR_TEXT_COLOR`, `INPUT_TEXT_COLOR`, `READY_STATUS_COLOR`, `THINKING_STATUS_COLOR`, `STATUS_BACKGROUND_COLOR`, `STATUS_BORDER_COLOR`, `BUTTON_BACKGROUND_COLOR`, `BUTTON_ACTIVE_BACKGROUND_COLOR`, `BUTTON_TEXT_COLOR`
- Padding/sizing: `TEXT_BOX_PAD_X`, `INPUT_TEXT_BOX_PAD_X`, `TEXT_BOX_PAD_Y`, `STATUS_WIDTH_CHARS`, `BUTTON_PAD_X`, `BUTTON_PAD_Y`, `BUTTON_WIDTH_CHARS`
- Fonts: `FONT_FAMILY`, `CHAT_FONT_SIZE_PT`, `INPUT_FONT_SIZE_PT`, `STATUS_FONT_SIZE_PT`, `BUTTON_FONT_SIZE_PT`
- Model: `OLLAMA_URL`, `OLLAMA_MODEL`, `REQUEST_TIMEOUT_SEC`, `SYSTEM_PROMPT_PATH`, `SYSTEM_PROMPT`, `TURN_INJECTIONS`
- Watchdog: `WATCHDOG_IDLE_SEC`, `WATCHDOG_MAX_REPLIES`, `WATCHDOG_ENABLED_AT_TURN`, `WATCHDOG_SYSTEM_PROMPT`, `WATCHDOG_USER_PROMPT`
- Local UI testing: `DUMMY_AI_REPLY_ENABLED`, `DUMMY_AI_REPLY_DELAY_SEC`, `DUMMY_AI_REPLY`, `PREFILL_USER_INPUT_ENABLED`, `PREFILL_USER_INPUT_TEXT`

`SYSTEM_PROMPT_PATH` points to the shared prompt document used by the UQ project profiles. `SYSTEM_PROMPT` is loaded from that file when the app starts. Turn injections are configured directly in `config.py` as a Python list so they stay easy to inspect and edit.

For layout testing without Ollama, set `DUMMY_AI_REPLY_ENABLED = True`. To prefill the participant input box with test text, set `PREFILL_USER_INPUT_ENABLED = True`. Turn both off before running a real session.

## Session Logs

Each app run creates a new folder under `sessions/` containing:

- `conversation_log.jsonl`
- `session_dialogue.txt`

## Notes

- The interface is intentionally locked while a reply is in progress.
- Escape and common close/hide/minimize shortcuts are ignored during the session.
- The default experimenter quit shortcut is Ctrl+Shift+Q.
- Reply generation runs in a background thread so the Tkinter window stays responsive while waiting.
- By default, the first turn includes an injection telling the assistant to introduce itself briefly and ask the participant for their name.
- By default, the watchdog becomes active from turn 1 and can send repeated re-engagement messages after each idle interval, up to the configured per-turn maximum.
