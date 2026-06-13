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

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Study Buddy AI 🤖", page_icon="🎓", layout="centered")

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .main { background: #0f0f1a; }
    .stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%); }

    .hero-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        text-align: center;
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    /* Subject cards */
    .subject-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }

    /* Thinking steps */
    .thinking-box {
        background: rgba(167, 139, 250, 0.08);
        border-left: 3px solid #a78bfa;
        border-radius: 0 12px 12px 0;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        color: #c4b5fd;
        font-size: 0.9rem;
    }

    /* Answer box */
    .answer-box {
        background: rgba(52, 211, 153, 0.08);
        border: 1px solid rgba(52, 211, 153, 0.3);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-top: 1rem;
        color: #d1fae5;
        font-size: 1rem;
        line-height: 1.7;
    }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .badge-ai   { background: rgba(167,139,250,0.2); color: #a78bfa; }
    .badge-step { background: rgba(96,165,250,0.2);  color: #60a5fa; }

    .stSelectbox label { color: #94a3b8 !important; }
    .stTextArea label  { color: #94a3b8 !important; }
    .stTextArea textarea {
        background: #1e1e2e !important;
        border: 1px solid rgba(167,139,250,0.4) !important;
        color: #f1f5f9 !important;
        caret-color: #f1f5f9 !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
    }
    .stTextArea textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    .stTextArea textarea:focus {
        border: 1px solid #a78bfa !important;
        box-shadow: 0 0 0 2px rgba(167,139,250,0.2) !important;
        outline: none !important;
    }
    /* Fix for Streamlit's internal textarea wrapper */
    div[data-baseweb="textarea"] {
        background: #1e1e2e !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="textarea"] textarea {
        background: #1e1e2e !important;
        color: #f1f5f9 !important;
        caret-color: #f1f5f9 !important;
    }

    div[data-testid="stButton"] button {
        width: 100%;
        background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.65rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        cursor: pointer;
    }

    .chat-user {
        background: rgba(96,165,250,0.12);
        border-radius: 12px 12px 4px 12px;
        padding: 0.7rem 1rem;
        color: #bfdbfe;
        margin: 0.4rem 0;
        text-align: right;
    }
    .chat-ai {
        background: rgba(52,211,153,0.08);
        border-radius: 12px 12px 12px 4px;
        padding: 0.7rem 1rem;
        color: #d1fae5;
        margin: 0.4rem 0;
        border-left: 3px solid #34d399;
    }
    .chat-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }
    .chat-label.user { color: #60a5fa; }
    .chat-label.ai   { color: #34d399; }

    hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ─── AZURE CONFIG ────────────────────────────────────────────────────────────────
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "regai_gpt_latest")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

SUBJECTS = {
    "📐 Mathematics": "math",
    "🔬 Science": "science",
    "📚 History": "history",
    "✍️ English": "english",
    "💻 Computer": "computer",
    "🌍 Geography": "geography",
}

SUBJECT_PROMPTS = {
    "math": "You are a friendly Math teacher for Indian Class 10 and 12 students. Explain step by step using simple Hindi-English (Hinglish). Use formulas clearly, give solved examples.",
    "science": "You are a friendly Science teacher for Indian Class 10 and 12 students. Explain Physics, Chemistry, Biology concepts simply. Use Hinglish, give real-life examples.",
    "history": "You are a friendly History teacher for Indian Class 10 and 12 students. Explain events, dates, causes and effects in simple Hinglish. Use stories to make it interesting.",
    "english": "You are a friendly English teacher for Indian Class 10 and 12 students. Help with grammar, essays, comprehension in simple language. Mix Hindi explanations where needed.",
    "computer": "You are a friendly Computer Science teacher for Indian Class 10 and 12 students. Explain programming, algorithms, hardware concepts simply in Hinglish with examples.",
    "geography": "You are a friendly Geography teacher for Indian Class 10 and 12 students. Explain maps, climate, resources in simple Hinglish with Indian examples.",
}

# ─── SESSION STATE ───────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "math"
if "qa_count" not in st.session_state:
    st.session_state.qa_count = 0


# ─── HELPER: CALL AZURE ─────────────────────────────────────────────────────────
def ask_ai(question: str, subject_key: str) -> str:
    if not AZURE_ENDPOINT or not AZURE_API_KEY:
        return "⚠️ Azure keys nahi mili! `.env` file mein AZURE_ENDPOINT aur AZURE_API_KEY set karo."

    system_prompt = SUBJECT_PROMPTS.get(subject_key, SUBJECT_PROMPTS["math"])

    # Build messages with history (last 6 turns for context)
    messages = [{"role": "system", "content": system_prompt}]
    for turn in st.session_state.chat_history[-6:]:
        messages.append({"role": "user", "content": turn["q"]})
        messages.append({"role": "assistant", "content": turn["a"]})
    messages.append({"role": "user", "content": question})

    url = f"{AZURE_ENDPOINT}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"
    payload = json.dumps(
        {
            "messages": messages,
            "max_tokens": 700,
            "temperature": 0.6,
            "stream": False,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "api-key": AZURE_API_KEY},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return f"❌ Azure Error {e.code}: {body}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ─── HERO ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🎓 Study Buddy AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Tumhara personal AI teacher — koi bhi sawaal poocho! 🚀</div>',
    unsafe_allow_html=True,
)

# ─── HOW AI WORKS EXPLAINER (collapsible) ────────────────────────────────────────
with st.expander("🤔 AI kaise sochta hai? (Click karke dekho!)"):
    st.markdown(
        """
    <div class="thinking-box">
        <span class="badge badge-step">Step 1 — Input</span><br>
        Tumhara sawaal AI ko text ke roop mein milta hai. Jaise: <em>"Newton ka 2nd law kya hai?"</em>
    </div>
    <div class="thinking-box">
        <span class="badge badge-step">Step 2 — Tokenization</span><br>
        AI tumhare sentence ko chhote-chhote <strong>tokens</strong> (words/parts) mein todta hai.
    </div>
    <div class="thinking-box">
        <span class="badge badge-step">Step 3 — Neural Network Processing</span><br>
        Billions of parameters ke through information process hoti hai — <strong>Deep Learning</strong>!
    </div>
    <div class="thinking-box">
        <span class="badge badge-step">Step 4 — Output Generation</span><br>
        AI ek-ek word predict karke jawab banata hai — yahi hai <strong>Generative AI</strong>!
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─── SUBJECT SELECTOR ────────────────────────────────────────────────────────────
st.markdown("#### 📖 Subject chuno:")
cols = st.columns(3)
subject_keys = list(SUBJECTS.keys())
for i, subj_label in enumerate(subject_keys):
    with cols[i % 3]:
        if st.button(subj_label, key=f"subj_{i}"):
            st.session_state.selected_subject = SUBJECTS[subj_label]
            st.session_state.chat_history = []

# Show current subject
current = [k for k, v in SUBJECTS.items() if v == st.session_state.selected_subject]
if current:
    st.markdown(
        f'<span class="badge badge-ai">✅ Current Subject: {current[0]}</span>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ─── CHAT HISTORY ────────────────────────────────────────────────────────────────
if st.session_state.chat_history:
    st.markdown("#### 💬 Conversation:")
    for turn in st.session_state.chat_history:
        st.markdown(
            f"""
        <div class="chat-user">
            <div class="chat-label user">👤 TUM</div>
            {turn['q']}
        </div>
        <div class="chat-ai">
            <div class="chat-label ai">🤖 STUDY BUDDY</div>
            {turn['a']}
        </div>
        """,
            unsafe_allow_html=True,
        )
    st.markdown("---")

# ─── INPUT ───────────────────────────────────────────────────────────────────────
question = st.text_area(
    "✏️ Apna sawaal yahan likho:",
    placeholder="Example: Newton ka second law kya hai? / Quadratic equation solve karo / What is photosynthesis?",
    height=100,
    key="question_input",
)

col1, col2 = st.columns([3, 1])
with col1:
    ask_btn = st.button("🚀 AI se Poocho!", use_container_width=True)
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ─── AI RESPONSE ─────────────────────────────────────────────────────────────────
if ask_btn and question.strip():
    st.markdown("---")
    st.markdown("#### 🧠 AI Soch Raha Hai...")

    # Show thinking animation
    steps = [
        "📥 Tumhara sawaal samajh raha hoon...",
        "🔍 Subject context load kar raha hoon...",
        "⚙️ Neural network process kar raha hai...",
        "✍️ Jawab generate ho raha hai...",
    ]
    progress = st.progress(0)
    status = st.empty()
    for idx, step in enumerate(steps):
        status.markdown(
            f'<div class="thinking-box">{step}</div>', unsafe_allow_html=True
        )
        progress.progress((idx + 1) * 20)
        time.sleep(0.5)

    # Actual API call
    answer = ask_ai(question.strip(), st.session_state.selected_subject)

    progress.progress(100)
    status.empty()

    # Save to history
    st.session_state.chat_history.append({"q": question.strip(), "a": answer})
    st.session_state.qa_count += 1

    # Show answer
    st.markdown(
        f"""
    <div class="answer-box">
        <span class="badge badge-ai">🤖 Study Buddy ka Jawab</span><br><br>
        {answer}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Fun stat
    st.success(f"✅ {st.session_state.qa_count} sawaal pooche gaye is session mein!")

elif ask_btn:
    st.warning("⚠️ Pehle koi sawaal likho!")

# ─── FOOTER ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
<div style='text-align:center; color:#475569; font-size:0.8rem;'>
    🤖 Powered by <strong>Azure OpenAI GPT-4o</strong> &nbsp;|&nbsp; 
    Built with <strong>Streamlit</strong> &nbsp;
</div>
""",
    unsafe_allow_html=True,
)
