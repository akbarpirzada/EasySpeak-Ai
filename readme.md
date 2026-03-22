# 🎙️ EasySpeach AI — Speech-to-Speech Assistant

> Record your voice → AI transcribes → AI replies → AI speaks back.  
> Built with **Streamlit**, **Faster-Whisper**, **Groq LLM**, and **gTTS / Piper TTS**.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎤 **Auto-run pipeline** | Fires automatically when you stop recording — no button click needed |
| 💬 **Chat UI** | Full conversation history with `st.chat_message` bubbles |
| 🔊 **Voice replies** | Every AI response includes a playable audio player inside the chat bubble |
| 🌐 **Multi-language** | Reply in 10 languages — English, Urdu, Arabic, French, Spanish, German, Hindi, Turkish, Chinese, Japanese |
| ⏱️ **Latency display** | ASR / LLM / TTS timing shown in the sidebar after every turn |
| 🛡️ **Validation** | Empty audio guard + VAD-based silence/noise filtering |
| 🔄 **Voice engine switch** | Choose between gTTS (online) or Piper (offline) from the sidebar |
| 🗑️ **Clear chat** | One-click session reset |

---

## 🏗️ Architecture

```
Your Voice (WAV)
      │
      ▼
 [1] ASR — Faster-Whisper (runs locally, CPU)
      │  transcript text
      ▼
 [2] LLM — Groq API (llama-3.1-8b-instant)
      │  reply text
      ▼
 [3] TTS — gTTS (online) or Piper (offline)
      │  audio bytes
      ▼
 Chat bubble (text + audio player)
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/akbarpirzada/EasySpeak_AI.git
cd voicebridge-ai
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your `.env` file

```bash
cp .env.example .env
```

Open `.env` and add your Groq API key (get one free at [console.groq.com](https://console.groq.com)):

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Run the app

```bash
streamlit run app.py
```

---

## ⚙️ Configuration (`.env`)

```env
# ── LLM ──────────────────────────────────────────────────────────
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL_ID=llama-3.1-8b-instant
SYSTEM_PROMPT="You are a helpful voice assistant. Keep replies short."

# ── ASR (Speech-to-Text) ─────────────────────────────────────────
# Model sizes: tiny.en | base.en | small.en | medium.en
# Use tiny.en on low-RAM machines
WHISPER_MODEL=base.en
WHISPER_LANGUAGE=en
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
WHISPER_CPU_THREADS=4

# ── TTS (Text-to-Speech) ─────────────────────────────────────────
# gtts  = online, lightweight
# piper = offline, neural (requires .onnx voice files)
TTS_ENGINE=gtts
GTTS_LANG=en

# Piper offline voices (only if TTS_ENGINE=piper)
PIPER_MODEL_PATH=voices/en_us-lessac-low.onnx
PIPER_CONFIG_PATH=voices/en_us-lessac-low.onnx.json
```

---

## 🌐 Supported Languages

| Language | gTTS Code | Whisper Code |
|----------|-----------|--------------|
| English  | `en`      | `en`         |
| Urdu     | `ur`      | `ur`         |
| Arabic   | `ar`      | `ar`         |
| French   | `fr`      | `fr`         |
| Spanish  | `es`      | `es`         |
| German   | `de`      | `de`         |
| Hindi    | `hi`      | `hi`         |
| Turkish  | `tr`      | `tr`         |
| Chinese  | `zh-CN`   | `zh`         |
| Japanese | `ja`      | `ja`         |

> **Tip:** You can speak in any language — Whisper auto-detects your voice. Select the reply language from the sidebar dropdown.

---

## 📦 Requirements

```
streamlit>=1.35.0
python-dotenv
requests
faster-whisper
gTTS
piper-tts        # optional — only for offline Piper voices
```

---

## 🗂️ Project Structure

```
voicebridge-ai/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .env                # Your config (never commit this!)
├── voices/             # Optional: Piper .onnx voice files
│   ├── en_us-lessac-low.onnx
│   └── en_us-lessac-low.onnx.json
└── README.md
```

---

## 🔌 Using Piper (Offline TTS)

1. Download a voice from [Piper Voices on HuggingFace](https://huggingface.co/rhasspy/piper-voices)
2. Place both `.onnx` and `.onnx.json` files inside the `voices/` folder
3. Set `TTS_ENGINE=piper` in your `.env`
4. The sidebar dropdown will auto-discover all available voices

---

## 💡 Tips

- **Low RAM machine?** Use `WHISPER_MODEL=tiny.en` in your `.env`
- **No internet?** Switch TTS engine to `piper` for fully offline voice synthesis
- **Slow responses?** Reduce `max_tokens` in `run_llm()` or switch to a smaller Whisper model

---

## 🙌 Acknowledgements

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | App framework |
| [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) | Speech recognition (ASR) |
| [Groq](https://groq.com) | Ultra-fast LLM inference |
| [gTTS](https://gtts.readthedocs.io) | Online text-to-speech |
| [Piper](https://github.com/rhasspy/piper) | Offline neural text-to-speech |

---

## 📄 License

MIT License — free to use, modify, and distribute.