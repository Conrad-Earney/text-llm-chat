import os
import json
from datetime import datetime


class SessionLogger:
    def __init__(self):
        # Ensure /sessions exists
        base_dir = os.path.join(os.path.dirname(__file__), "sessions")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Create timestamped session folder
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(base_dir, f"session_{ts}")
        os.makedirs(self.session_dir)

        # Path for the conversation log
        self.log_path = os.path.join(self.session_dir, "conversation_log.jsonl")

        self.turn = 0

    def log_turn(self, user_text, ai_text):
        self.turn += 1
        record = {
            "turn": self.turn,
            "timestamp": datetime.now().isoformat(),
            "user_text": user_text,
            "assistant_text": ai_text
        }
        with open(self.log_path, "a") as f:
            json.dump(record, f)
            f.write("\n")
