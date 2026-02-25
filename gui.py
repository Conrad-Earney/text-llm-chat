import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

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

    # --- Top bar with New Chat + Close ---
    top_bar = tk.Frame(container)
    top_bar.pack(fill="x", pady=5)

    def new_chat():
        chat_box.configure(state="normal")
        chat_box.delete("1.0", tk.END)
        chat_box.configure(state="disabled")

    new_chat_button = ttk.Button(top_bar, text="New Chat", command=new_chat)
    new_chat_button.pack(side="left", padx=5)

    close_button = ttk.Button(top_bar, text="Close", command=root.destroy)
    close_button.pack(side="right", padx=5)

    # --- Chat history display (scrollable) ---
    chat_box = ScrolledText(container, width=80, height=25,
                            wrap="word", state="disabled")
    chat_box.pack(pady=10, fill="both", expand=True)

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

    # --- Sending logic ---
    def on_send(event=None):
        user_text = input_box.get("1.0", tk.END).strip()
        if not user_text:
            return

        # Show user message
        add_chat_message("You", user_text)
        input_box.delete("1.0", tk.END)

        # AI reply
        reply = generate_reply(user_text)
        add_chat_message("AI", reply)

        # Log turn
        logger.log_turn(user_text, reply)

    # Enter key to send
    root.bind("<Return>", on_send)
    send_button.config(command=on_send)

    # --- Start UI loop ---
    root.mainloop()


if __name__ == "__main__":
    main()
