import tkinter as tk
import re
import threading
from datetime import datetime

from chat_logic import generate_reply
import config as cfg
from conversation import ConversationState
from session_logger import SessionLogger


_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_BLOCKED_SHORTCUTS = (
    "q",
    "w",
    "h",
    "m",
    "n",
    "o",
    "s",
    "p",
    "r",
    "l",
    "t",
    "a",
    "c",
    "v",
    "x",
    "grave",
    "comma",
    "period",
    "slash",
)


def _enter_fullscreen(root):
    root.attributes("-fullscreen", True)
    root.lift()


def _sanitize_user_text(raw_text):
    text = str(raw_text or "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2028", "\n").replace("\u2029", "\n")
    text = _CONTROL_CHARS_RE.sub("", text)

    lines = []
    blank_count = 0
    for line in text.split("\n"):
        line = line.strip()
        if line:
            blank_count = 0
            lines.append(line)
            continue
        if blank_count < 1:
            lines.append("")
        blank_count += 1

    text = "\n".join(lines).strip()
    if len(text) > cfg.MAX_USER_INPUT_CHARS:
        text = text[:cfg.MAX_USER_INPUT_CHARS].rstrip()
    return text


def _format_message_for_display(text):
    lines = str(text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [line.strip() for line in lines]
    return "\n".join(line for line in lines if line).strip()


def _make_scrollable_text(parent, width, height, font, fg, pad_x=cfg.TEXT_BOX_PAD_X):
    frame = tk.Frame(
        parent,
        bg=cfg.TEXT_BOX_BORDER_COLOR,
        relief="solid",
        borderwidth=1,
        highlightthickness=0,
    )
    text = tk.Text(
        frame,
        width=width,
        height=height,
        wrap="word",
        font=font,
        bg=cfg.TEXT_BOX_BACKGROUND_COLOR,
        fg=fg,
        insertbackground=cfg.INPUT_TEXT_COLOR,
        selectbackground="#C8D8F0",
        selectforeground=fg,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        padx=pad_x,
        pady=cfg.TEXT_BOX_PAD_Y,
    )
    scrollbar = tk.Scrollbar(
        frame,
        orient="vertical",
        command=text.yview,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
    )
    text.configure(yscrollcommand=scrollbar.set)
    text.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    return frame, text


def main():
    root = tk.Tk()
    root.title(cfg.APP_TITLE)

    _enter_fullscreen(root)
    chat_font = (cfg.FONT_FAMILY, cfg.CHAT_FONT_SIZE_PT)
    input_font = (cfg.FONT_FAMILY, cfg.INPUT_FONT_SIZE_PT)
    status_font = (cfg.FONT_FAMILY, cfg.STATUS_FONT_SIZE_PT)
    button_font = (cfg.FONT_FAMILY, cfg.BUTTON_FONT_SIZE_PT)

    def swallow_event(event=None):
        return "break"

    def quit_app(event=None):
        cancel_watchdog()
        root.destroy()
        return "break"

    if root.tk.call("tk", "windowingsystem") == "aqua":
        root.createcommand("tk::mac::Quit", swallow_event)
        root.createcommand("tk::mac::ShowPreferences", swallow_event)

    root.protocol("WM_DELETE_WINDOW", swallow_event)
    root.bind_all("<Escape>", swallow_event)
    for shortcut in cfg.EXPERIMENTER_QUIT_SHORTCUTS:
        root.bind_all(shortcut, quit_app)
    for key in _BLOCKED_SHORTCUTS:
        root.bind_all("<Command-{}>".format(key), swallow_event)
        if key != "q":
            root.bind_all("<Control-{}>".format(key), swallow_event)

    # --- Center container frame ---
    root.configure(bg=cfg.APP_BACKGROUND_COLOR)
    container = tk.Frame(root, bg=cfg.APP_BACKGROUND_COLOR)
    container.place(relx=0.5, rely=0.5, anchor="center")

    # --- Initialize logger ---
    logger = SessionLogger()
    conversation = ConversationState()

    # --- Chat history display (scrollable) ---
    chat_frame, chat_box = _make_scrollable_text(
        container,
        width=cfg.CHAT_WIDTH_CHARS,
        height=cfg.CHAT_HEIGHT_LINES,
        font=chat_font,
        fg=cfg.ASSISTANT_TEXT_COLOR,
    )
    chat_box.configure(state="disabled")
    chat_frame.grid(row=0, column=0, pady=(0, cfg.CHAT_STATUS_GAP_PX))
    chat_box.tag_configure(
        "assistant_message",
        justify="left",
        foreground=cfg.ASSISTANT_TEXT_COLOR,
        rmargin=cfg.CHAT_TEXT_MARGIN_PX,
        spacing1=2,
        spacing3=0,
    )
    chat_box.tag_configure(
        "user_message",
        justify="left",
        foreground=cfg.USER_TEXT_COLOR,
        rmargin=cfg.USER_MESSAGE_RIGHT_MARGIN_PX,
        spacing1=2,
        spacing3=0,
    )
    chat_box.tag_configure(
        "error_message",
        justify="left",
        foreground=cfg.ERROR_TEXT_COLOR,
        rmargin=cfg.CHAT_TEXT_MARGIN_PX,
        spacing1=2,
        spacing3=0,
    )
    chat_box.tag_configure(
        "message_gap",
        spacing3=cfg.MESSAGE_SPACING_AFTER_PX,
    )

    def update_chat_message_margins(event=None):
        user_left_margin = max(
            cfg.CHAT_TEXT_MARGIN_PX,
            int(chat_box.winfo_width() * cfg.USER_MESSAGE_LEFT_MARGIN_FRACTION),
        )
        chat_box.tag_configure(
            "user_message",
            lmargin1=user_left_margin,
            lmargin2=user_left_margin,
        )

    chat_box.bind("<Configure>", update_chat_message_margins)
    root.after_idle(update_chat_message_margins)

    def add_chat_message(role, text):
        tag = "user_message" if role == "You" else "assistant_message"
        if str(text or "").startswith("ERROR:"):
            tag = "error_message"
        display_text = _format_message_for_display(text)
        chat_box.configure(state="normal")
        chat_box.insert(tk.END, "{}\n".format(display_text), tag)
        chat_box.insert(tk.END, "\n", "message_gap")
        chat_box.configure(state="disabled")
        chat_box.see(tk.END)

    # --- Input area ---
    input_frame = tk.Frame(container, bg=cfg.APP_BACKGROUND_COLOR)
    input_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew")

    input_box_frame, input_box = _make_scrollable_text(
        input_frame,
        height=cfg.INPUT_HEIGHT_LINES,
        width=cfg.INPUT_WIDTH_CHARS,
        font=input_font,
        fg=cfg.INPUT_TEXT_COLOR,
        pad_x=cfg.INPUT_TEXT_BOX_PAD_X,
    )
    input_box_frame.grid(row=0, column=0, sticky="ew")
    if cfg.PREFILL_USER_INPUT_ENABLED:
        input_box.insert("1.0", cfg.PREFILL_USER_INPUT_TEXT)

    control_frame = tk.Frame(input_frame, bg=cfg.APP_BACKGROUND_COLOR)
    control_frame.grid(row=0, column=1, padx=(10, 0), sticky="ns")

    send_button = tk.Button(
        control_frame,
        text="Send",
        font=button_font,
        width=cfg.BUTTON_WIDTH_CHARS,
        padx=cfg.BUTTON_PAD_X,
        pady=cfg.BUTTON_PAD_Y,
        relief="raised",
        borderwidth=1,
        bg=cfg.BUTTON_BACKGROUND_COLOR,
        fg=cfg.BUTTON_TEXT_COLOR,
        activebackground=cfg.BUTTON_ACTIVE_BACKGROUND_COLOR,
        activeforeground=cfg.BUTTON_TEXT_COLOR,
        disabledforeground="#777777",
        highlightthickness=0,
        highlightbackground=cfg.APP_BACKGROUND_COLOR,
    )
    send_button.configure(
        background=cfg.BUTTON_BACKGROUND_COLOR,
        foreground=cfg.BUTTON_TEXT_COLOR,
    )
    send_button.grid(row=0, column=0, pady=(0, cfg.BUTTON_STATUS_GAP_PX // 2), sticky="nsew")

    status_label = tk.Label(
        control_frame,
        text="Ready",
        fg=cfg.READY_STATUS_COLOR,
        bg=cfg.STATUS_BACKGROUND_COLOR,
        font=status_font,
        width=cfg.STATUS_WIDTH_CHARS,
        anchor="center",
        relief="solid",
        borderwidth=1,
        highlightthickness=0,
        highlightbackground=cfg.STATUS_BORDER_COLOR,
    )
    status_label.grid(row=1, column=0, pady=(cfg.BUTTON_STATUS_GAP_PX // 2, 0), sticky="nsew")

    def set_status(text, color):
        status_label.config(text=text, fg=color)
        status_label.update_idletasks()

    input_frame.grid_columnconfigure(0, weight=1)
    control_frame.grid_columnconfigure(0, weight=1)
    control_frame.grid_rowconfigure(0, weight=1, uniform="control_stack")
    control_frame.grid_rowconfigure(1, weight=1, uniform="control_stack")
    container.grid_columnconfigure(0, weight=1)

    current_turn_started_at = None
    reply_in_progress = False
    watchdog_after_id = None
    watchdog_in_progress = False
    watchdog_reply_count_for_turn = 0

    def on_input_modified(event=None):
        nonlocal current_turn_started_at
        if current_turn_started_at is None:
            current_turn_started_at = datetime.now()
        cancel_watchdog()

    def enforce_input_limit(event=None):
        text = input_box.get("1.0", "end-1c")
        if len(text) <= cfg.MAX_USER_INPUT_CHARS:
            return
        input_box.delete("1.0 + {} chars".format(cfg.MAX_USER_INPUT_CHARS), tk.END)
        input_box.bell()

    def on_input_key_release(event=None):
        enforce_input_limit()
        if input_box.get("1.0", tk.END).strip():
            return
        schedule_watchdog()

    def set_interaction_enabled(enabled):
        input_state = "normal" if enabled else "disabled"
        button_state = "normal" if enabled else "disabled"
        input_box.configure(state=input_state)
        send_button.config(state=button_state)

    def cancel_watchdog():
        nonlocal watchdog_after_id
        if watchdog_after_id is not None:
            root.after_cancel(watchdog_after_id)
            watchdog_after_id = None

    def schedule_watchdog():
        nonlocal watchdog_after_id
        cancel_watchdog()
        if reply_in_progress or watchdog_in_progress:
            return
        if cfg.WATCHDOG_IDLE_SEC <= 0:
            return
        if conversation.turn_count < cfg.WATCHDOG_ENABLED_AT_TURN:
            return
        if cfg.WATCHDOG_MAX_REPLIES >= 0 and watchdog_reply_count_for_turn >= cfg.WATCHDOG_MAX_REPLIES:
            return
        if not conversation.has_assistant_history():
            return
        watchdog_after_id = root.after(int(cfg.WATCHDOG_IDLE_SEC * 1000), on_watchdog_timeout)

    def complete_turn(user_text, turn_started_at, user_sent_at, ai_started_at, reply, ai_finished_at):
        nonlocal current_turn_started_at, reply_in_progress
        add_chat_message("AI", reply)
        conversation.add_assistant_message(reply)

        logger.log_turn(
            user_text=user_text,
            ai_text=reply,
            turn_started_at=turn_started_at,
            user_sent_at=user_sent_at,
            ai_started_at=ai_started_at,
            ai_finished_at=ai_finished_at,
        )

        current_turn_started_at = None
        reply_in_progress = False
        set_interaction_enabled(True)
        set_status("Ready", cfg.READY_STATUS_COLOR)
        schedule_watchdog()

    def complete_watchdog_turn(reply, ai_started_at, ai_finished_at):
        nonlocal watchdog_in_progress, watchdog_reply_count_for_turn
        add_chat_message("AI", reply)
        conversation.add_assistant_message(reply)
        logger.log_watchdog_turn(
            ai_text=reply,
            ai_started_at=ai_started_at,
            ai_finished_at=ai_finished_at,
        )
        watchdog_in_progress = False
        watchdog_reply_count_for_turn += 1
        set_status("Ready", cfg.READY_STATUS_COLOR)
        schedule_watchdog()

    def complete_initial_turn(reply, ai_started_at, ai_finished_at):
        nonlocal reply_in_progress, current_turn_started_at
        add_chat_message("AI", reply)
        if not str(reply or "").startswith("ERROR:"):
            conversation.add_assistant_message(reply)
        logger.log_initial_turn(
            ai_text=reply,
            ai_started_at=ai_started_at,
            ai_finished_at=ai_finished_at,
        )
        current_turn_started_at = None
        reply_in_progress = False
        set_interaction_enabled(True)
        set_status("Ready", cfg.READY_STATUS_COLOR)
        input_box.focus_set()

    def generate_reply_async(user_text, turn_started_at, user_sent_at, messages):
        ai_started_at = datetime.now()
        reply = generate_reply(messages)
        ai_finished_at = datetime.now()
        root.after(
            0,
            complete_turn,
            user_text,
            turn_started_at,
            user_sent_at,
            ai_started_at,
            reply,
            ai_finished_at,
        )

    def generate_initial_reply_async(messages):
        ai_started_at = datetime.now()
        reply = generate_reply(messages)
        ai_finished_at = datetime.now()
        root.after(
            0,
            complete_initial_turn,
            reply,
            ai_started_at,
            ai_finished_at,
        )

    def generate_watchdog_reply_async(messages):
        ai_started_at = datetime.now()
        reply = generate_reply(messages)
        ai_finished_at = datetime.now()
        root.after(
            0,
            complete_watchdog_turn,
            reply,
            ai_started_at,
            ai_finished_at,
        )

    def on_watchdog_timeout():
        nonlocal watchdog_after_id, watchdog_in_progress
        watchdog_after_id = None
        if reply_in_progress or watchdog_in_progress:
            return
        if input_box.get("1.0", tk.END).strip():
            return
        if not conversation.has_assistant_history():
            return

        watchdog_in_progress = True
        set_status("Thinking...", cfg.THINKING_STATUS_COLOR)
        messages = conversation.build_watchdog_messages()
        threading.Thread(
            target=generate_watchdog_reply_async,
            args=(messages,),
            daemon=True,
        ).start()

    # --- Sending logic ---
    def on_send(event=None):
        nonlocal current_turn_started_at, reply_in_progress, watchdog_reply_count_for_turn
        if reply_in_progress:
            return

        user_text = _sanitize_user_text(input_box.get("1.0", tk.END))
        if not user_text:
            input_box.delete("1.0", tk.END)
            return

        user_sent_at = datetime.now()
        turn_started_at = current_turn_started_at or user_sent_at
        reply_in_progress = True
        watchdog_reply_count_for_turn = 0

        # Show user message
        add_chat_message("You", user_text)
        conversation.add_user_message(user_text)
        request_messages = conversation.build_turn_messages()
        input_box.delete("1.0", tk.END)
        input_box.edit_modified(False)

        set_interaction_enabled(False)
        set_status("Thinking...", cfg.THINKING_STATUS_COLOR)

        threading.Thread(
            target=generate_reply_async,
            args=(user_text, turn_started_at, user_sent_at, request_messages),
            daemon=True,
        ).start()

    def start_initial_turn():
        nonlocal reply_in_progress
        reply_in_progress = True
        set_interaction_enabled(False)
        set_status("Thinking...", cfg.THINKING_STATUS_COLOR)
        messages = conversation.build_initial_assistant_messages()
        threading.Thread(
            target=generate_initial_reply_async,
            args=(messages,),
            daemon=True,
        ).start()

    def on_enter_send(event=None):
        on_send(event)
        return "break"

    input_box.bind("<KeyPress>", on_input_modified)
    input_box.bind("<KeyRelease>", on_input_key_release)
    input_box.bind("<Return>", on_enter_send)
    input_box.bind("<KP_Enter>", on_enter_send)
    for shortcut in ("<Command-a>", "<Command-A>", "<Control-a>", "<Control-A>"):
        input_box.bind(shortcut, swallow_event)
    for shortcut in ("<Command-c>", "<Command-C>", "<Control-c>", "<Control-C>"):
        input_box.bind(shortcut, swallow_event)
    for shortcut in ("<Command-v>", "<Command-V>", "<Control-v>", "<Control-V>"):
        input_box.bind(shortcut, swallow_event)
    for shortcut in ("<Command-x>", "<Command-X>", "<Control-x>", "<Control-X>"):
        input_box.bind(shortcut, swallow_event)
    input_box.bind("<<Paste>>", swallow_event)
    input_box.bind("<<Cut>>", swallow_event)
    input_box.bind("<<Copy>>", swallow_event)

    send_button.config(command=on_send)
    root.after(0, start_initial_turn)

    # --- Start UI loop ---
    root.mainloop()


if __name__ == "__main__":
    main()
