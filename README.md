# 🎓 Study Buddy AI — Deployment Guide

## Step 1 — Files taiyar karo
```
study_buddy/
├── app.py
├── requirements.txt
└── .env.example  →  isko .env mein rename karo
```

## Step 2 — .env file banao
`.env.example` ko copy karo, naam badal ke `.env` karo aur apni Azure keys bharo:
```
AZURE_ENDPOINT=https://your-resource.openai.azure.com
AZURE_API_KEY=abc123...
AZURE_DEPLOYMENT=gpt-4o
AZURE_API_VERSION=2024-02-01
```

## Step 3 — Local test (optional)
```bash
pip install streamlit
streamlit run app.py
```
Browser mein http://localhost:8501 khulega.

---

## 🌐 Streamlit Cloud pe Deploy (FREE Live URL ke liye)

### A) GitHub pe upload karo
1. GitHub.com par nayi **public repository** banao (e.g. `study-buddy-ai`)
2. `app.py` aur `requirements.txt` upload karo (`.env` mat upload karna — secret hai!)

### B) Streamlit Cloud connect karo
1. **share.streamlit.io** par jao
2. "New app" → apni GitHub repo select karo
3. Main file: `app.py`

### C) Secrets set karo (Azure keys)
Streamlit Cloud mein:
```
Settings → Secrets → yeh paste karo:

AZURE_ENDPOINT = "https://your-resource.openai.azure.com"
AZURE_API_KEY = "your-key-here"
AZURE_DEPLOYMENT = "gpt-4o"
AZURE_API_VERSION = "2024-02-01"
```

### D) Deploy!
"Deploy" button dabao — 2-3 minute mein live URL milega jaise:
`https://your-name-study-buddy.streamlit.app`

---

## Demo Script (Class ke liye)
1. **"AI kya hai?"** — Expander khol ke dikhao AI ke 4 steps
2. **Subject choose karo** — Science ya Math
3. **Sawaal poocho** — "Newton ka 2nd law kya hai?"
4. **Thinking animation dikhao** — "Dekho AI kaise step by step sochta hai!"
5. **Jawab padhao** — Students se pucho "Samajh aaya?"
6. **Follow-up** — "Iska example do" — AI history use karta hai!
