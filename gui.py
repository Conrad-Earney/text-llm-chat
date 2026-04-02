import tkinter as tk
import os
import re
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

from chat_logic import generate_reply
from session_logger import SessionLogger


WINDOWED_FALLBACK_GEOMETRY = "1280x800+80+80"


def _signed_offset(value):
    return "+{}".format(value) if value >= 0 else str(value)


def _format_geometry(width, height, x, y):
    return "{}x{}{}{}".format(width, height, _signed_offset(x), _signed_offset(y))


def _parse_geometry_override(raw_value):
    raw_value = (raw_value or "").strip()
    if not raw_value:
        return None

    match = re.fullmatch(r"(\d+)x(\d+)([+-]\d+)([+-]\d+)", raw_value)
    if not match:
        return None

    width_text, height_text, x_text, y_text = match.groups()
    return (
        max(200, int(width_text)),
        max(200, int(height_text)),
        int(x_text),
        int(y_text),
    )


def _best_external_geometry(root):
    root.update_idletasks()

    screen_w = int(root.winfo_screenwidth())
    screen_h = int(root.winfo_screenheight())
    vroot_x = int(root.winfo_vrootx())
    vroot_y = int(root.winfo_vrooty())
    vroot_w = int(root.winfo_vrootwidth())
    vroot_h = int(root.winfo_vrootheight())

    virtual_left = vroot_x
    virtual_top = vroot_y
    virtual_right = vroot_x + vroot_w
    virtual_bottom = vroot_y + vroot_h

    candidates = []

    if virtual_left < 0:
        candidates.append((0 - virtual_left, screen_h, virtual_left, 0))
    if virtual_right > screen_w:
        candidates.append((virtual_right - screen_w, screen_h, screen_w, 0))
    if virtual_top < 0:
        candidates.append((screen_w, 0 - virtual_top, 0, virtual_top))
    if virtual_bottom > screen_h:
        candidates.append((screen_w, virtual_bottom - screen_h, 0, screen_h))

    candidates = [candidate for candidate in candidates if candidate[0] >= 400 and candidate[1] >= 300]
    if not candidates:
        return None

    return max(candidates, key=lambda candidate: candidate[0] * candidate[1])


def _enter_presentation_display(root, bounds_override_env):
    override = _parse_geometry_override(os.getenv(bounds_override_env))
    if override is not None:
        width, height, x, y = override
    else:
        target = _best_external_geometry(root)
        if target is None:
            root.geometry(WINDOWED_FALLBACK_GEOMETRY)
            return False
        width, height, x, y = target

    root.attributes("-fullscreen", False)
    root.overrideredirect(True)
    root.geometry(_format_geometry(width, height, x, y))
    root.lift()
    return True


def main():
    root = tk.Tk()
    root.title("Text Chat")

    presentation_mode = _enter_presentation_display(root, "TEXT_LLM_CHAT_DISPLAY_BOUNDS")

    def on_escape(event=None):
        if presentation_mode:
            root.overrideredirect(False)
            root.geometry(WINDOWED_FALLBACK_GEOMETRY)
        else:
            root.attributes("-fullscreen", False)

    root.bind("<Escape>", on_escape)

    # --- Center container frame ---
    container = tk.Frame(root)
    container.place(relx=0.5, rely=0.5, anchor="center")

    # --- Initialize logger ---
    logger = SessionLogger()

    status_label = ttk.Label(container, text="Ready", foreground="green")
    status_label.pack(pady=(0, 10))

    # --- Chat history display (scrollable) ---
    chat_box = ScrolledText(container, width=80, height=25,
                            wrap="word", state="disabled")
    chat_box.pack(pady=10, fill="both", expand=True)

    def set_status(text, color):
        status_label.config(text=text, foreground=color)
        status_label.update_idletasks()

    def add_chat_message(role, text):
        chat_box.configure(state="normal")
        chat_box.insert(tk.END, f"{role}: {text}\n\n")
        chat_box.configure(state="disabled")
        chat_box.see(tk.END)

    # --- Input area ---
    input_frame = tk.Frame(container)
    input_frame.pack(fill="x", pady=10)

    input_box = ScrolledText(input_frame, height=4, width=60, wrap="word")
    input_box.pack(side="left", fill="both", expand=True)

    send_button = ttk.Button(input_frame, text="Send")
    send_button.pack(side="left", padx=10)

    current_turn_started_at = None

    def on_input_modified(event=None):
        nonlocal current_turn_started_at
        if current_turn_started_at is None:
            current_turn_started_at = datetime.now()

    # --- Sending logic ---
    def on_send(event=None):
        nonlocal current_turn_started_at
        user_text = input_box.get("1.0", tk.END).strip()
        if not user_text:
            return

        user_sent_at = datetime.now()
        turn_started_at = current_turn_started_at or user_sent_at

        input_box.configure(state="disabled")
        send_button.config(state="disabled")
        set_status("Waiting for AI reply...", "blue")

        # Show user message
        add_chat_message("You", user_text)
        input_box.configure(state="normal")
        input_box.delete("1.0", tk.END)
        input_box.edit_modified(False)
        input_box.configure(state="disabled")

        # AI reply
        ai_started_at = datetime.now()
        reply = generate_reply(user_text)
        ai_finished_at = datetime.now()
        add_chat_message("AI", reply)

        # Log turn
        logger.log_turn(
            user_text=user_text,
            ai_text=reply,
            turn_started_at=turn_started_at,
            user_sent_at=user_sent_at,
            ai_started_at=ai_started_at,
            ai_finished_at=ai_finished_at,
        )

        current_turn_started_at = None
        input_box.configure(state="normal")
        send_button.config(state="normal")
        set_status("Ready", "green")

    input_box.bind("<KeyPress>", on_input_modified)

    send_button.config(command=on_send)

    # --- Start UI loop ---
    root.mainloop()


if __name__ == "__main__":
    main()
