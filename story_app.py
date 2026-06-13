import streamlit as st
import urllib.request
import urllib.error
import json
import os
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Story Generator ✨",
    page_icon="📖",
    layout="centered"
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0d0d1a 0%, #1a0a2e 100%); }

    .hero-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #f472b6, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }
    .story-box {
        background: rgba(244,114,182,0.06);
        border: 1px solid rgba(244,114,182,0.25);
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        color: #fce7f3;
        font-size: 1.05rem;
        line-height: 1.9;
        white-space: pre-wrap;
    }
    .twist-box {
        background: rgba(167,139,250,0.1);
        border-left: 4px solid #a78bfa;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        color: #e9d5ff;
        font-size: 1rem;
        margin-top: 1rem;
        font-style: italic;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .badge-pink   { background: rgba(244,114,182,0.2); color: #f472b6; }
    .badge-purple { background: rgba(167,139,250,0.2); color: #a78bfa; }
    .badge-blue   { background: rgba(96,165,250,0.2);  color: #60a5fa; }

    .genre-btn button {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
    }

    div[data-testid="stButton"] button {
        width: 100%;
        background: linear-gradient(90deg, #be185d, #7c3aed) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 0.7rem !important;
    }
    .stTextInput input, .stTextArea textarea {
        background: #1a0a2e !important;
        border: 1px solid rgba(167,139,250,0.4) !important;
        color: #f1f5f9 !important;
        caret-color: #f1f5f9 !important;
        border-radius: 10px !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #64748b !important;
    }
    .stSelectbox > div > div {
        background: #1a0a2e !important;
        border: 1px solid rgba(167,139,250,0.4) !important;
        color: #f1f5f9 !important;
        border-radius: 10px !important;
    }
    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #94a3b8 !important;
    }
    .stRadio label { color: #cbd5e1 !important; }
    .stRadio div[role="radiogroup"] label { color: #cbd5e1 !important; }

    .stat-row {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    .stat-chip {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 0.4rem 0.8rem;
        color: #94a3b8;
        font-size: 0.82rem;
    }
    hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ─── AZURE CONFIG ────────────────────────────────────────────────────────────
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_API_KEY  = os.getenv("AZURE_OPENAI_API_KEY",  "")
DEPLOYMENT     = os.getenv("AZURE_OPENAI_DEPLOYMENT", "regai_gpt_latest")
API_VERSION    = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

# ─── SESSION STATE ───────────────────────────────────────────────────────────
if "stories"       not in st.session_state: st.session_state.stories       = []
if "selected_genre" not in st.session_state: st.session_state.selected_genre = "Adventure"

GENRES = ["🏔️ Adventure", "👻 Horror", "💕 Romance", "🔬 Sci-Fi", "🧙 Fantasy", "😂 Comedy", "🕵️ Mystery"]

# ─── AI FUNCTION ─────────────────────────────────────────────────────────────
def generate_story(topic: str, genre: str, language: str, length: str) -> str:
    if not AZURE_ENDPOINT or not AZURE_API_KEY:
        return "⚠️ Azure keys nahi mili! Streamlit Secrets mein keys set karo."

    length_map = {"Short (1 min read)": "200", "Medium (3 min read)": "400", "Long (5 min read)": "700"}
    words      = length_map.get(length, "300")

    lang_map = {
        "🇮🇳 Hinglish": "Hinglish (mix of Hindi and English, written in English script)",
        "🇬🇧 English":  "pure English",
        "🇮🇳 Hindi":    "pure Hindi written in Devanagari script",
    }
    lang_instruction = lang_map.get(language, "Hinglish")

    system_prompt = f"""You are a creative storyteller for Indian school students (Class 10 and 12).
Write engaging stories in {lang_instruction}.
Always end with a surprising TWIST that the reader won't expect.
Keep language simple and fun. Use vivid descriptions.
Format: Write the story first, then on a new line write "🌀 TWIST:" followed by the twist ending."""

    user_prompt = f"Write a {genre.split()[-1]} story about: {topic}\nLength: approximately {words} words."

    url     = f"{AZURE_ENDPOINT}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"
    payload = json.dumps({
        "messages":    [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        "max_tokens":  900,
        "temperature": 0.9,
    }).encode("utf-8")

    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json", "api-key": AZURE_API_KEY},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"❌ Azure Error {e.code}: {e.read().decode('utf-8')}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">✨ AI Story Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Koi bhi topic do — AI ek poori kahani likhega with a surprise twist! 🌀</div>', unsafe_allow_html=True)

# ─── HOW IT WORKS ─────────────────────────────────────────────────────────────
with st.expander("🤖 AI Story kaise likhta hai? (Click karo!)"):
    st.markdown("""
    <div style="color:#94a3b8; line-height:1.8; font-size:0.92rem;">
        <b style="color:#f472b6;">Step 1 — Prompt Engineering:</b> Tumhara topic + genre ek special instruction mein convert hota hai<br>
        <b style="color:#a78bfa;">Step 2 — Context Window:</b> AI poora scene apne "memory" mein rakhta hai<br>
        <b style="color:#60a5fa;">Step 3 — Token Generation:</b> Ek ek word predict hota hai — billions of parameters se!<br>
        <b style="color:#34d399;">Step 4 — Temperature = 0.9:</b> High creativity mode — isliye har baar nai kahani! 🎲
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── GENRE SELECTOR ───────────────────────────────────────────────────────────
st.markdown("#### 🎭 Genre chuno:")
cols = st.columns(4)
for i, genre in enumerate(GENRES):
    with cols[i % 4]:
        if st.button(genre, key=f"g_{i}"):
            st.session_state.selected_genre = genre

st.markdown(f'<span class="badge badge-purple">✅ Genre: {st.session_state.selected_genre}</span>', unsafe_allow_html=True)

st.markdown("---")

# ─── INPUTS ───────────────────────────────────────────────────────────────────
topic = st.text_input(
    "📝 Story ka topic likho:",
    placeholder="e.g. Ek student jisko time travel ki machine mili / A robot who wants to be human"
)

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox("🌐 Language:", ["🇮🇳 Hinglish", "🇬🇧 English", "🇮🇳 Hindi"])
with col2:
    length = st.selectbox("📏 Story length:", ["Short (1 min read)", "Medium (3 min read)", "Long (5 min read)"])

generate_btn = st.button("✨ Story Generate Karo!")

# ─── GENERATE ─────────────────────────────────────────────────────────────────
if generate_btn and topic.strip():
    st.markdown("---")
    st.markdown("#### 🖊️ AI likh raha hai...")

    steps = [
        "💭 Topic samajh raha hoon...",
        "🎭 Genre aur mood set kar raha hoon...",
        "✍️ Characters create ho rahe hain...",
        "🌀 Twist soch raha hoon (shhh! secret hai)...",
        "📖 Story likhi ja rahi hai...",
    ]
    progress = st.progress(0)
    status   = st.empty()
    for idx, step in enumerate(steps):
        status.markdown(f'<div style="color:#a78bfa; padding:0.5rem; font-size:0.9rem;">{step}</div>', unsafe_allow_html=True)
        progress.progress((idx + 1) * 16)
        time.sleep(0.5)

    raw = generate_story(topic.strip(), st.session_state.selected_genre, language, length)
    progress.progress(100)
    status.empty()

    # Split story and twist
    if "🌀 TWIST:" in raw:
        parts      = raw.split("🌀 TWIST:", 1)
        story_text = parts[0].strip()
        twist_text = parts[1].strip()
    else:
        story_text = raw
        twist_text = ""

    # Word count
    word_count = len(raw.split())
    st.session_state.stories.append({
        "topic": topic.strip(),
        "genre": st.session_state.selected_genre,
        "story": story_text,
        "twist": twist_text,
    })

    # Display
    st.markdown(f'<span class="badge badge-pink">📖 {st.session_state.selected_genre} Story</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="story-box">{story_text}</div>', unsafe_allow_html=True)

    if twist_text:
        st.markdown(f'<div class="twist-box"><b>🌀 TWIST:</b> {twist_text}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-chip">📝 ~{word_count} words</div>
        <div class="stat-chip">🌐 {language}</div>
        <div class="stat-chip">🎭 {st.session_state.selected_genre}</div>
        <div class="stat-chip">📚 Total stories: {len(st.session_state.stories)}</div>
    </div>
    """, unsafe_allow_html=True)

elif generate_btn:
    st.warning("⚠️ Pehle topic likho!")

# ─── STORY HISTORY ────────────────────────────────────────────────────────────
if len(st.session_state.stories) > 1:
    st.markdown("---")
    st.markdown("#### 📚 Aaj ki stories:")
    for i, s in enumerate(reversed(st.session_state.stories[:-1]), 1):
        with st.expander(f"📖 {s['genre']} — {s['topic'][:40]}..."):
            st.markdown(f'<div class="story-box" style="font-size:0.9rem;">{s["story"]}</div>', unsafe_allow_html=True)
            if s["twist"]:
                st.markdown(f'<div class="twist-box">🌀 {s["twist"]}</div>', unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#475569; font-size:0.8rem;'>
    ✨ Powered by <strong>Azure OpenAI</strong> &nbsp;|&nbsp;
    Built with <strong>Streamlit</strong> &nbsp;|&nbsp;
    <em>AI Demo for Class 10 &amp; 12 Students</em>
</div>
""", unsafe_allow_html=True)