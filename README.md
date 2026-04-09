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

Main settings:

- `APP_TITLE`
- `WINDOWED_FALLBACK_GEOMETRY`
- `DISPLAY_BOUNDS_OVERRIDE`
- `OLLAMA_URL`
- `OLLAMA_MODEL`
- `REQUEST_TIMEOUT_SEC`
- `SYSTEM_PROMPT`
- `TURN_INJECTIONS`
- `WATCHDOG_IDLE_SEC`
- `WATCHDOG_MAX_REPLIES`
- `WATCHDOG_ENABLED_AT_TURN`
- `WATCHDOG_SYSTEM_PROMPT`
- `WATCHDOG_USER_PROMPT`
- `SESSIONS_DIRNAME`

Turn injections are configured directly in `config.py` as a Python list so they stay easy to inspect and edit.

## Session Logs

Each app run creates a new folder under `sessions/` containing:

- `conversation_log.jsonl`
- `session_dialogue.txt`

## Notes

- The interface is intentionally locked while a reply is in progress.
- Reply generation runs in a background thread so the Tkinter window stays responsive while waiting.
- By default, the first turn includes an injection telling the assistant to introduce itself briefly and ask the participant for their name.
- By default, the watchdog becomes active from turn 1 and can send repeated re-engagement messages after each idle interval, up to the configured per-turn maximum.
