# 🤖 DeepSeek-Chat-GUI 💬

A Python-based **DeepSeek AI Desktop Chat Application** that allows you to **chat with DeepSeek AI models directly from a modern GUI** — built with CustomTkinter.
This project is designed as a **learning lab** to improve:
- GUI application development with CustomTkinter
- API & session handling logic
- HTTP request handling & response parsing
- AES-based cookie authentication
- Multithreading in Python desktop apps

It is especially useful for **exploring AI models**, **GUI tool development**, and **understanding how web sessions and authentication work**.

---

## 🧱 Project Structure

```bash
deepseek-chat-gui/
│
├── assets/                 # Screenshots
├── main.py                 # Main GUI application
├── LICENSE
└── README.md               # Project documentation
```

---

## ✨ Features

### 🤖 Multi-Model Support
- Choose from **18 DeepSeek AI models** via a sidebar dropdown
- Includes DeepSeek-V1 through V3, R1, Prover, Coder, and more
- Switch models mid-conversation instantly

### 💬 Modern Chat Interface
- **Bubble-style chat UI** — user messages on right, AI responses on left
- Real-time **"🧠 AI is thinking..."** indicator while waiting for response
- Tracks query count per session in the sidebar stats

### 🎨 Elegant Dark Theme GUI
- Fully custom dark theme powered by `customtkinter`
- Sidebar with live connection status badge, model selector, and session stats
- Color-coded bubbles for user, AI, and system messages

### ⚡ Threaded & Non-Blocking
- UI never freezes during API calls
- Background threading for session initialization and message queries

### 🔧 Extra Controls
- **⟳ Reconnect** — reinitialize session without restarting the app
- **🗑 Clear Chat** — wipe conversation and start fresh
- **Enter** to send • **Shift+Enter** for new line

---

## 🛠 Technologies Used

| Technology | Role |
| --- | --- |
| **Python 3** | Core programming language |
| **customtkinter** | Modern dark-themed desktop GUI |
| **requests** | HTTP session & API communication |
| **pycryptodome** | AES cookie decryption for session auth |
| **threading** | Non-blocking background API calls |
| **regex (re)** | HTML response parsing |

---

## 📌 Requirements

```bash
Python 3.7+
```

Install required libraries:

```bash
pip install customtkinter requests pycryptodome
```

---

## ▶️ How to Run

### 1️⃣ Clone the repository

```bash
git clone https://github.com/ShakalBhau0001/deepseek-chat-gui.git
```

### 2️⃣ Enter the project directory

```bash
cd deepseek-chat-gui
```

### 3️⃣ Install dependencies

```bash
pip install customtkinter requests pycryptodome
```

### 4️⃣ Run the app

```bash
python main.py
```

---

## 🖥️ Usage

After launching, the app auto-connects and opens the chat window:

```
┌──────────────────────┬──────────────────────────────────────┐
│  🤖 Sidebar          │  💬 Chat with DeepSeek-V3            │
│                      │                                      │
│  🟢 Connected        │               You: What is Python?   │
│                      │                                      │
│  Model: DeepSeek-V3  │  🤖 DeepSeek-V3:                    │
│  Queries: 1          │  Python is a high-level...           │
│                      │                                      │
│  [🗑 Clear Chat]     │  [ Type your message...      ]  ➤   │
│  [⟳ Reconnect  ]     │                                      │
└──────────────────────┴──────────────────────────────────────┘
```

### 💬 Chat Example

**You type:**
```
What is machine learning?
```

**AI responds in a bubble:**
```
🤖 DeepSeek-V3
Machine learning is a subset of artificial intelligence...
```

---

## ⚙️ How It Works

### 1️⃣ Session Initialization
- A `requests.Session` is created with a browser-like User-Agent
- The app connects to the proxy server and solves an **AES-based cookie challenge** to authenticate the session
- Runs in a **background thread** so the UI stays fully responsive

### 2️⃣ Model Selection
- User picks a model from the sidebar dropdown
- Selected model is passed with each request to the backend
- Model can be switched at any time during conversation

### 3️⃣ Chat Loop
- User message is sent via HTTP POST to the proxy in a background thread
- Response HTML is parsed using regex to extract the AI reply
- Reply is displayed in a styled chat bubble with the model name

---

## ⚠️ Limitations

- Requires an active internet connection
- Dependent on third-party proxy server availability
- Model names may not reflect exact backend models
- Not suitable for sensitive or confidential conversations

---

## 🌟 Future Enhancements

- Conversation history saving to `.txt` or `.md`
- Light / dark theme toggle
- Direct Official DeepSeek API support
- Multi-turn context memory
- Copy button on each chat bubble
- Font size customization

---

## ⚠️ Disclaimer

> **Please read carefully before use.**

- This is an **unofficial, community-made project** and is **NOT affiliated with DeepSeek AI** in any way.
- This tool routes requests through a **third-party proxy server** (`asmodeus.free.nf`), which is **not controlled** by the developer of this project.
- **Do NOT enter any personal, sensitive, financial, or confidential information** while using this tool.
- All conversations **may be logged** by the third-party proxy server operator. The developer takes **no responsibility** for any data shared.
- The model names listed are for selection purposes only and may not reflect exact backend models.
- This project is intended for **educational and personal use only**.
- For production or professional use, please use the [Official DeepSeek API](https://platform.deepseek.com/).

---

## 🪪 Author

> **Creator: Shakal Bhau**

> **GitHub: [ShakalBhau0001](https://github.com/ShakalBhau0001)**

---
