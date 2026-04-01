import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

from chat_logic import generate_reply
from session_logger import SessionLogger


def main():
    root = tk.Tk()
    root.title("Text Chat")

    # --- Fullscreen & Escape to exit fullscreen ---
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

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
