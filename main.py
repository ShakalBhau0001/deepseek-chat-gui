import requests
import re
import time
import threading
import customtkinter as ctk
import tkinter as tk
from Crypto.Cipher import AES

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#0a0d14"
BG2 = "#12151f"
BG3 = "#1a1e2e"
BG4 = "#222840"
ACCENT = "#7c6ef7"
ACCENT2 = "#5a4fd4"
GREEN = "#00e676"
RED = "#ff5252"
YELLOW = "#ffd740"
CYAN = "#00e5ff"
TEXT = "#e8eaf6"
TEXT_DIM = "#6c7293"
BORDER = "#2d3154"

MODELS = [
    "DeepSeek-V1",
    "DeepSeek-V2",
    "DeepSeek-V2.5",
    "DeepSeek-V3",
    "DeepSeek-V3-0324",
    "DeepSeek-V3.1",
    "DeepSeek-V3.2",
    "DeepSeek-R1",
    "DeepSeek-R1-0528",
    "DeepSeek-R1-Distill",
    "DeepSeek-Prover-V1",
    "DeepSeek-Prover-V1.5",
    "DeepSeek-Prover-V2",
    "DeepSeek-VL",
    "DeepSeek-Coder",
    "DeepSeek-Coder-V2",
    "DeepSeek-Coder-6.7B-base",
    "DeepSeek-Coder-6.7B-instruct",
]


# ── Session Initialise and Query Functions
def init_session():
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Android 12; Mobile; rv:97.0) Gecko/97.0 Firefox/97.0"
        }
    )
    r = s.get("https://asmodeus.free.nf/")
    nums = re.findall(r'toNumbers\("([a-f0-9]+)"\)', r.text)
    key, iv, data = [bytes.fromhex(n) for n in nums[:3]]
    s.cookies.set(
        "__test",
        AES.new(key, AES.MODE_CBC, iv).decrypt(data).hex(),
        domain="asmodeus.free.nf",
    )
    s.get("https://asmodeus.free.nf/index.php?i=1")
    time.sleep(0.5)
    return s


def ask_deepseek(session, model, question):
    r = session.post(
        "https://asmodeus.free.nf/deepseek.php",
        params={"i": "1"},
        data={"model": model, "question": question},
    )
    match = re.search(r'<div class="response-content">(.*?)</div>', r.text, re.DOTALL)
    return match.group(1).strip() if match else "⚠ No response received."


# ── Main App
class DeepSeekApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🤖 DeepSeek AI Chat")
        self.geometry("1000x700")
        self.minsize(800, 560)
        self.configure(fg_color=BG)
        self.resizable(True, True)
        self.session = None
        self.model = tk.StringVar(value=MODELS[3])  # DeepSeek-V3 default
        self.msg_count = 0
        self.is_connected = False
        self._build_ui()
        self.after(400, self._init_session_thread)

    # ── Build UI
    def _build_ui(self):
        # ── Left sidebar
        sidebar = ctk.CTkFrame(self, fg_color=BG2, corner_radius=0, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(sidebar, fg_color=BG3, corner_radius=12)
        logo_frame.pack(fill="x", padx=12, pady=(16, 8))

        ctk.CTkLabel(
            logo_frame,
            text="🤖",
            font=ctk.CTkFont(size=32),
        ).pack(pady=(12, 2))
        ctk.CTkLabel(
            logo_frame,
            text="DeepSeek AI",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=ACCENT,
        ).pack()
        ctk.CTkLabel(
            logo_frame,
            text="by Shakal Bhau",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=TEXT_DIM,
        ).pack(pady=(0, 12))

        # Status badge
        self.status_badge = ctk.CTkLabel(
            sidebar,
            text="⏳  Connecting...",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=YELLOW,
            fg_color=BG3,
            corner_radius=8,
            padx=10,
            pady=6,
        )
        self.status_badge.pack(fill="x", padx=12, pady=(0, 12))

        # Model selector label
        ctk.CTkLabel(
            sidebar,
            text="SELECT MODEL",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=TEXT_DIM,
        ).pack(anchor="w", padx=16, pady=(4, 2))

        # Model dropdown
        self.model_menu = ctk.CTkOptionMenu(
            sidebar,
            values=MODELS,
            variable=self.model,
            fg_color=BG3,
            button_color=ACCENT2,
            button_hover_color=ACCENT,
            text_color=TEXT,
            dropdown_fg_color=BG3,
            dropdown_text_color=TEXT,
            dropdown_hover_color=BG4,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=8,
            command=self._on_model_change,
        )
        self.model_menu.pack(fill="x", padx=12, pady=(0, 12))

        # Stats
        stats = ctk.CTkFrame(sidebar, fg_color=BG3, corner_radius=10)
        stats.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkLabel(
            stats,
            text="SESSION STATS",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=TEXT_DIM,
        ).pack(anchor="w", padx=12, pady=(10, 4))

        self.stat_queries = self._sidebar_stat(stats, "Queries", "0", CYAN)
        self.stat_model = self._sidebar_stat(stats, "Active Model", "V3", ACCENT)

        # Clear button
        ctk.CTkButton(
            sidebar,
            text="🗑  Clear Chat",
            fg_color=BG4,
            hover_color="#ff524222",
            text_color=RED,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=8,
            height=36,
            command=self._clear_chat,
        ).pack(fill="x", padx=12, pady=(4, 4))

        # Reconnection button
        ctk.CTkButton(
            sidebar,
            text="⟳  Reconnect",
            fg_color=BG4,
            hover_color="#00e67622",
            text_color=GREEN,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=8,
            height=36,
            command=self._init_session_thread,
        ).pack(fill="x", padx=12, pady=(0, 4))

        # Footer
        ctk.CTkLabel(
            sidebar,
            text="github.com/ShakalBhau0001",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=TEXT_DIM,
        ).pack(side="bottom", pady=10)

        # ── Right chat area
        chat_area = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        chat_area.pack(side="right", fill="both", expand=True)

        # Top bar
        topbar = ctk.CTkFrame(chat_area, fg_color=BG2, corner_radius=0, height=52)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        self.topbar_model_lbl = ctk.CTkLabel(
            topbar,
            text=f"💬  Chat with {self.model.get()}",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=TEXT,
        )
        self.topbar_model_lbl.pack(side="left", padx=20, pady=14)

        self.thinking_lbl = ctk.CTkLabel(
            topbar,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=YELLOW,
        )
        self.thinking_lbl.pack(side="right", padx=16)

        # Chat display
        self.chat_frame = ctk.CTkScrollableFrame(
            chat_area,
            fg_color=BG,
            corner_radius=0,
            scrollbar_button_color=BG3,
            scrollbar_button_hover_color=ACCENT2,
        )
        self.chat_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Input area
        input_area = ctk.CTkFrame(chat_area, fg_color=BG2, corner_radius=0, height=80)
        input_area.pack(fill="x", side="bottom")
        input_area.pack_propagate(False)

        self.input_box = ctk.CTkTextbox(
            input_area,
            height=52,
            fg_color=BG3,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            corner_radius=10,
            wrap="word",
        )
        self.input_box.pack(side="left", fill="x", expand=True, padx=(16, 8), pady=14)
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<Shift-Return>", self._on_shift_enter)

        self.send_btn = ctk.CTkButton(
            input_area,
            text="Send  ➤",
            width=100,
            height=52,
            fg_color=ACCENT2,
            hover_color=ACCENT,
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=10,
            command=self._send_message,
        )
        self.send_btn.pack(side="right", padx=(0, 16), pady=14)

        # Welcome bubble
        self._add_system_bubble(
            "👋 Welcome! Select a model from the sidebar and start chatting.\n"
            "Press Enter to send • Shift+Enter for new line."
        )

    def _sidebar_stat(self, parent, label, value, color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_DIM,
        ).pack(side="left")
        val_lbl = ctk.CTkLabel(
            row,
            text=value,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=color,
        )
        val_lbl.pack(side="right", pady=(0, 2))
        return val_lbl

    # ── Chat Bubbles
    def _add_user_bubble(self, text):
        outer = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        outer.pack(fill="x", pady=(6, 2), padx=16)

        ctk.CTkLabel(
            outer,
            text="You",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=CYAN,
        ).pack(anchor="e")

        bubble = ctk.CTkFrame(outer, fg_color=ACCENT2, corner_radius=12)
        bubble.pack(anchor="e", ipadx=2)

        ctk.CTkLabel(
            bubble,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="white",
            wraplength=520,
            justify="left",
        ).pack(padx=14, pady=10)

        self._scroll_to_bottom()

    def _add_ai_bubble(self, text, model_name):
        outer = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        outer.pack(fill="x", pady=(2, 6), padx=16)

        ctk.CTkLabel(
            outer,
            text=f"🤖  {model_name}",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w")

        bubble = ctk.CTkFrame(outer, fg_color=BG3, corner_radius=12)
        bubble.pack(anchor="w", ipadx=2)

        ctk.CTkLabel(
            bubble,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT,
            wraplength=520,
            justify="left",
        ).pack(padx=14, pady=10)

        self._scroll_to_bottom()

    def _add_system_bubble(self, text):
        outer = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        outer.pack(fill="x", pady=4, padx=16)

        ctk.CTkLabel(
            outer,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_DIM,
            justify="center",
        ).pack(anchor="center")

    def _scroll_to_bottom(self):
        self.after(100, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))

    # ── Session Initialise
    def _init_session_thread(self):
        self.is_connected = False
        self.send_btn.configure(state="disabled")
        self.status_badge.configure(text="⏳  Connecting...", text_color=YELLOW)
        self._add_system_bubble("⏳ Initializing AI session...")
        threading.Thread(target=self._init_session_worker, daemon=True).start()

    def _init_session_worker(self):
        try:
            self.session = init_session()
            self.after(0, self._on_connected)
        except Exception as e:
            self.after(0, lambda: self._on_connect_failed(str(e)))

    def _on_connected(self):
        self.is_connected = True
        self.send_btn.configure(state="normal")
        self.status_badge.configure(text="🟢  Connected", text_color=GREEN)
        self._add_system_bubble(f"✅ Session ready! Chatting with {self.model.get()}")

    def _on_connect_failed(self, err):
        self.status_badge.configure(text="🔴  Offline", text_color=RED)
        self._add_system_bubble(
            f"❌ Connection failed: {err}\nClick ⟳ Reconnect to try again."
        )

    # ── Sending Message
    def _on_enter(self, event):
        self._send_message()
        return "break"

    def _on_shift_enter(self, event):
        return None

    def _send_message(self):
        if not self.is_connected:
            self._add_system_bubble("❌ Not connected. Click ⟳ Reconnect.")
            return

        msg = self.input_box.get("1.0", "end").strip()
        if not msg:
            return

        self.input_box.delete("1.0", "end")
        self._add_user_bubble(msg)
        self.send_btn.configure(state="disabled")
        self.thinking_lbl.configure(text="🧠 AI is thinking...")
        threading.Thread(target=self._query_worker, args=(msg,), daemon=True).start()

    def _query_worker(self, msg):
        model = self.model.get()
        try:
            reply = ask_deepseek(self.session, model, msg)
        except Exception as e:
            reply = f"❌ Error: {str(e)}"

        self.msg_count += 1
        self.after(0, lambda: self._on_reply(reply, model))

    def _on_reply(self, reply, model):
        self._add_ai_bubble(reply, model)
        self.send_btn.configure(state="normal")
        self.thinking_lbl.configure(text="")
        self.stat_queries.configure(text=str(self.msg_count))

    # ── Model Change
    def _on_model_change(self, value):
        self.topbar_model_lbl.configure(text=f"💬  Chat with {value}")
        short = value.replace("DeepSeek-", "")
        self.stat_model.configure(text=short)
        self._add_system_bubble(f"🔄 Switched to {value}")

    # ── Clearing Chat
    def _clear_chat(self):
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        self.msg_count = 0
        self.stat_queries.configure(text="0")
        self._add_system_bubble("🗑 Chat cleared. Start a new conversation!")


# ── Entry Point
if __name__ == "__main__":
    app = DeepSeekApp()
    app.mainloop()
