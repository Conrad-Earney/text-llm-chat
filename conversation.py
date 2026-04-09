from config import SYSTEM_PROMPT, TURN_INJECTIONS, WATCHDOG_SYSTEM_PROMPT, WATCHDOG_USER_PROMPT


class ConversationState:
    def __init__(
        self,
        system_prompt=SYSTEM_PROMPT,
        turn_injections=None,
        watchdog_system_prompt=WATCHDOG_SYSTEM_PROMPT,
        watchdog_user_prompt=WATCHDOG_USER_PROMPT,
    ):
        self.system_prompt = str(system_prompt or "").strip()
        self.turn_injections = list(turn_injections or TURN_INJECTIONS)
        self.watchdog_system_prompt = str(watchdog_system_prompt or "").strip()
        self.watchdog_user_prompt = str(watchdog_user_prompt or "").strip()
        self.history = []
        self.turn_count = 0

    def add_user_message(self, text):
        content = str(text or "").strip()
        if not content:
            return
        self.history.append({"role": "user", "content": content})
        self.turn_count += 1

    def add_assistant_message(self, text):
        content = str(text or "").strip()
        if not content:
            return
        self.history.append({"role": "assistant", "content": content})

    def has_assistant_history(self):
        return any(message["role"] == "assistant" for message in self.history)

    def _active_injection_texts(self):
        texts = []
        for injection in self.turn_injections:
            if not isinstance(injection, dict):
                continue
            text = str(injection.get("text", "")).strip()
            if not text:
                continue
            at_turn = injection.get("at_turn")
            start_turn = injection.get("start_turn")
            end_turn = injection.get("end_turn")

            is_active = False
            if at_turn is not None:
                is_active = self.turn_count == at_turn
            elif start_turn is not None and end_turn is None:
                is_active = self.turn_count >= start_turn
            elif start_turn is not None and end_turn is not None:
                is_active = start_turn <= self.turn_count <= end_turn

            if is_active:
                texts.append(text)
        return texts

    def _base_messages(self):
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        for text in self._active_injection_texts():
            messages.append({"role": "system", "content": text})
        messages.extend(self.history)
        return messages

    def build_turn_messages(self):
        return list(self._base_messages())

    def build_watchdog_messages(self):
        messages = self._base_messages()
        if self.watchdog_system_prompt:
            messages.append({"role": "system", "content": self.watchdog_system_prompt})
        if self.watchdog_user_prompt:
            messages.append({"role": "user", "content": self.watchdog_user_prompt})
        return messages
