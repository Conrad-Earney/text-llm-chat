import os
import json
from datetime import datetime


class SessionLogger:
    def __init__(self):
        # Ensure /sessions exists
        base_dir = os.path.join(os.path.dirname(__file__), "sessions")
        os.makedirs(base_dir, exist_ok=True)

        # Create timestamped session folder
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(base_dir, f"session_{ts}")
        os.makedirs(self.session_dir, exist_ok=True)

        # Paths for session outputs
        self.log_path = os.path.join(self.session_dir, "conversation_log.jsonl")
        self.dialogue_path = os.path.join(self.session_dir, "session_dialogue.txt")

        self.turn = 0
        self.session_started_at = datetime.now()
        self.last_ai_timestamp = None

    def _log(self, record):
        with open(self.log_path, "a", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False)
            f.write("\n")

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

                    lines.append(self._dialogue_line(turn_id, "user", record.get("user_text", "")))
                    lines.append(self._dialogue_line(turn_id, "assistant", record.get("assistant_text", "")))

        dialogue_text = "\n\n\n".join(lines)
        if dialogue_text:
            dialogue_text += "\n\n\n"
        self._atomic_write_text(self.dialogue_path, dialogue_text)

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
            "participant_duration_sec": participant_response_time_sec,
            "ai_duration_sec": ai_response_time_sec,
            "user_text": user_text,
            "assistant_text": ai_text,
        }

        self._log(record)
        self._rewrite_session_dialogue()
        self.last_ai_timestamp = ai_finished_at
