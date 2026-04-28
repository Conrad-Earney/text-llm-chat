import os
import json
import shutil
from datetime import datetime

from config import SESSION_ARCHIVE_DIR, SESSIONS_DIRNAME


class SessionLogger:
    def __init__(self):
        base_dir = os.path.join(os.path.dirname(__file__), SESSIONS_DIRNAME)
        os.makedirs(base_dir, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = f"session_{ts}"
        self.session_dir = os.path.join(base_dir, session_name)
        os.makedirs(self.session_dir, exist_ok=True)

        archive_base_dir = os.path.abspath(os.path.expanduser(SESSION_ARCHIVE_DIR))
        self.archive_session_dir = os.path.join(archive_base_dir, session_name)
        os.makedirs(self.archive_session_dir, exist_ok=True)

        self.log_path = os.path.join(self.session_dir, "conversation_log.jsonl")
        self.dialogue_path = os.path.join(self.session_dir, "session_dialogue.txt")

        self.turn = 0
        self.session_started_at = datetime.now()
        self.last_ai_timestamp = None

    def _copy_session_to_archive(self):
        for filename in os.listdir(self.session_dir):
            src_path = os.path.join(self.session_dir, filename)
            if os.path.isfile(src_path):
                dst_path = os.path.join(self.archive_session_dir, filename)
                shutil.copy2(src_path, dst_path)

    def _log(self, record):
        with open(self.log_path, "a", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False)
            f.write("\n")
        self._copy_session_to_archive()

    def _atomic_write_text(self, final_path, text):
        tmp_path = final_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp_path, final_path)

    def _dialogue_line(self, turn_id, speaker, text):
        safe_text = "" if text is None else str(text)
        return "turn_{} {}: {}".format(int(turn_id), speaker, json.dumps(safe_text, ensure_ascii=False))

    def _rewrite_session_dialogue(self):
        lines = []
        if os.path.isfile(self.log_path):
            with open(self.log_path, "r", encoding="utf-8") as f:
                for raw_line in f:
                    raw_line = raw_line.strip()
                    if not raw_line:
                        continue
                    try:
                        record = json.loads(raw_line)
                    except Exception:
                        continue

                    turn_id = record.get("turn")
                    if turn_id is None:
                        continue

                    event_type = str(record.get("event_type", "participant")).strip().lower()
                    if event_type == "participant":
                        lines.append(self._dialogue_line(turn_id, "user", record.get("user_text", "")))
                    lines.append(self._dialogue_line(turn_id, "assistant", record.get("assistant_text", "")))

        dialogue_text = "\n\n\n".join(lines)
        if dialogue_text:
            dialogue_text += "\n\n\n"
        self._atomic_write_text(self.dialogue_path, dialogue_text)
        self._copy_session_to_archive()

    def log_turn(self, user_text, ai_text, turn_started_at, user_sent_at, ai_started_at, ai_finished_at):
        self.turn += 1

        participant_response_time_sec = None
        if self.last_ai_timestamp is None:
            participant_response_time_sec = (user_sent_at - turn_started_at).total_seconds()
        else:
            participant_response_time_sec = (user_sent_at - self.last_ai_timestamp).total_seconds()

        ai_response_time_sec = (ai_finished_at - ai_started_at).total_seconds()

        record = {
            "turn": self.turn,
            "event_type": "participant",
            "participant_duration_sec": participant_response_time_sec,
            "ai_duration_sec": ai_response_time_sec,
            "user_text": user_text,
            "assistant_text": ai_text,
        }

        self._log(record)
        self._rewrite_session_dialogue()
        self.last_ai_timestamp = ai_finished_at

    def log_watchdog_turn(self, ai_text, ai_started_at, ai_finished_at):
        self.turn += 1

        ai_response_time_sec = (ai_finished_at - ai_started_at).total_seconds()

        record = {
            "turn": self.turn,
            "event_type": "watchdog",
            "participant_duration_sec": None,
            "ai_duration_sec": ai_response_time_sec,
            "user_text": "",
            "assistant_text": ai_text,
        }

        self._log(record)
        self._rewrite_session_dialogue()
        self.last_ai_timestamp = ai_finished_at
