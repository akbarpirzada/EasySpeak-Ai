"""
SpeakEasy AI – Speech-to-Speech AI  |  Assignment 13
✅ Auto-run  ✅ Chat bubbles  ✅ Clear chat  ✅ Latency  ✅ Validation  ✅ Voice switch
"""
import os
import tempfile
import time
import hashlib
import requests
import wave
import streamlit as st
from dotenv import load_dotenv
from faster_whisper import WhisperModel  # Added for the load_whisper function
from gtts import gTTS

# Only import Piper if the engine is selected to avoid unnecessary overhead
# (Handled inside the run_tts function for portability)

# ── Initial Setup ─────────────────────────────────────────────────────────────
load_dotenv()
st.set_page_config(page_title="SpeakEasy AI", page_icon="🎙️", layout="centered")

# ── Config from .env ──────────────────────────────────────────────────────────
GROQ_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL  = os.getenv("GROQ_MODEL_ID", "llama-3.1-8b-instant")
SYS_PROMPT  = os.getenv("SYSTEM_PROMPT", "You are a helpful voice assistant. Keep replies short.")
W_MODEL     = os.getenv("WHISPER_MODEL", "base.en")
W_LANG      = os.getenv("WHISPER_LANGUAGE", "en")
W_DEVICE    = os.getenv("WHISPER_DEVICE", "cpu")
W_COMPUTE   = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
W_THREADS   = int(os.getenv("WHISPER_CPU_THREADS", "4"))
GTTS_LANG   = os.getenv("GTTS_LANG", "en")

# ── Session state ─────────────────────────────────────────────────────────────
st.session_state.setdefault("history", [])   # [{role, content, audio?, mime?}]
st.session_state.setdefault("latency", [])   # [{asr, llm, tts}]
st.session_state.setdefault("last_hash", "") # prevents re-running same clip

# ── Cached model ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading Whisper…")
def load_whisper():
    return WhisperModel(W_MODEL, device=W_DEVICE, compute_type=W_COMPUTE, cpu_threads=W_THREADS)

# ── Pipeline helpers ──────────────────────────────────────────────────────────
def run_asr(wav: bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav); path = f.name
    t0 = time.perf_counter()
    segs, _ = load_whisper().transcribe(path, language=W_LANG, beam_size=1, vad_filter=True)
    text = " ".join(s.text for s in segs).strip()
    os.remove(path)
    return text, round(time.perf_counter() - t0, 2)

def run_llm(user_text: str):
    t0 = time.perf_counter()
    if not GROQ_KEY:
        return f"⚠️ No API key. You said: {user_text}", 0.0
    lang_instruction = f" Always reply in {lang_name}."
    msgs = [{"role": "system", "content": SYS_PROMPT + lang_instruction}]
    msgs += [{"role": m["role"], "content": m["content"]} for m in st.session_state.history[-6:]]
    msgs += [{"role": "user", "content": user_text}]
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                      headers={"Authorization": f"Bearer {GROQ_KEY}"},
                      json={"model": GROQ_MODEL, "messages": msgs, "max_tokens": 250}, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip(), round(time.perf_counter() - t0, 2)

def run_tts(text: str, engine: str, lang: str, piper_model="", piper_cfg=""):
    t0 = time.perf_counter()
    if engine == "piper" and piper_model:
        from piper import PiperVoice
        v = PiperVoice.load(piper_model, piper_cfg)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f: path = f.name
        with wave.open(path, "wb") as wf: v.synthesize_wav(text, wf)
        audio = open(path, "rb").read(); os.remove(path)
        return audio, "audio/wav", round(time.perf_counter() - t0, 2)
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f: path = f.name
    gTTS(text=text, lang=lang).save(path)
    audio = open(path, "rb").read(); os.remove(path)
    return audio, "audio/mpeg", round(time.perf_counter() - t0, 2)

# ── Supported languages  {display: (gtts_code, whisper_code)} ────────────────
LANGUAGES = {
    "English"    : ("en", "en"),
    "Urdu"       : ("ur", "ur"),
    "Arabic"     : ("ar", "ar"),
    "French"     : ("fr", "fr"),
    "Spanish"    : ("es", "es"),
    "German"     : ("de", "de"),
    "Hindi"      : ("hi", "hi"),
    "Turkish"    : ("tr", "tr"),
    "Chinese"    : ("zh-CN", "zh"),
    "Japanese"   : ("ja", "ja"),
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎙️ SpeakEasy AI")
    st.caption("Speech · LLM · Speech")
    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.history = []
        st.session_state.latency = []
        st.session_state.last_hash = ""
        st.rerun()

    st.divider()
    st.subheader("🌐 Language")
    lang_name  = st.selectbox("Reply language", list(LANGUAGES.keys()), index=0)
    gtts_code, whisper_code = LANGUAGES[lang_name]

    st.divider()
    st.subheader("Voice Engine")
    engine   = st.selectbox("TTS", ["gtts", "piper"], index=0)
    tts_lang = gtts_code   # always driven by language selector
    p_model  = os.getenv("PIPER_MODEL_PATH", "") if engine == "piper" else ""
    p_cfg    = os.getenv("PIPER_CONFIG_PATH", "") if engine == "piper" else ""

    st.divider()
    st.caption(f"**Model:** {W_MODEL} · **LLM:** {GROQ_MODEL}")
    st.caption(f"**API:** {'✅ Connected' if GROQ_KEY else '❌ No key'}")

    if st.session_state.latency:
        st.divider()
        st.subheader("⏱️ Last Turn")
        l = st.session_state.latency[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric("ASR", f"{l['asr']}s")
        c2.metric("LLM", f"{l['llm']}s")
        c3.metric("TTS", f"{l['tts']}s")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("🎙️ SpeakEasy AI")
st.caption("Record → Transcribe → Reply → Speak")
st.divider()

# Chat bubbles — text + voice for assistant
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and "audio" in msg:
            st.audio(msg["audio"], format=msg["mime"])

st.divider()
audio = st.audio_input("🔴 Record your voice — pipeline runs automatically on stop")

# Auto-run — hash prevents re-firing on same clip
if audio:
    audio_hash = hashlib.md5(audio.getvalue()).hexdigest()
    if audio_hash != st.session_state.last_hash:
        st.session_state.last_hash = audio_hash

        with st.status("Running pipeline…", expanded=True) as status:
            st.write("🎤 Transcribing…")
            try:
                text, t_asr = run_asr(audio.getvalue())
            except Exception as e:
                st.error(f"ASR failed: {e}"); st.stop()

            if not text:
                st.warning("No speech detected. Please try again."); st.stop()

            st.write(f"📝 You said: *{text}*")
            st.write("🤖 Generating reply…")
            reply, t_llm = run_llm(text)

            st.write("🔊 Synthesising voice…")
            audio_out, mime, t_tts = run_tts(reply, engine, tts_lang, p_model, p_cfg)
            status.update(label="✅ Done!", state="complete")

        st.session_state.history += [
            {"role": "user",      "content": text},
            {"role": "assistant", "content": reply, "audio": audio_out, "mime": mime},
        ]
        st.session_state.latency.append({"asr": t_asr, "llm": t_llm, "tts": t_tts})
        st.rerun()
