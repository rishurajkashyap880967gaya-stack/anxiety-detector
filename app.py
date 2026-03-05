"""
app.py  –  Streamlit frontend for the Exam Anxiety Detector (Gemini AI edition).

Run
---
    streamlit run app.py
"""

import streamlit as st
import requests
import time

# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────
API_URL   = "http://localhost:8000/predict"
MAX_CHARS = 2000

COLOR_HEX = {
    "Low Anxiety":      "#2ecc71",
    "Moderate Anxiety": "#f39c12",
    "High Anxiety":     "#e74c3c",
}
BG_HEX = {
    "Low Anxiety":      "#eafaf1",
    "Moderate Anxiety": "#fef9e7",
    "High Anxiety":     "#fdedec",
}
EMOJIS_MAP = {
    "Low Anxiety":      "😌",
    "Moderate Anxiety": "😟",
    "High Anxiety":     "😰",
}

# ──────────────────────────────────────────────────────────────────────────────
# Page setup
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Exam Anxiety Detector · Gemini AI",
    page_icon  = "🧠",
    layout     = "centered",
)

st.markdown("""
<style>
body { font-family: 'Segoe UI', sans-serif; }

.result-card {
    border-radius: 14px;
    padding: 24px 28px;
    margin-top: 18px;
    border-left: 7px solid;
}
.reasoning-box {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.92rem;
    color: #444;
    margin-top: 10px;
    border-left: 4px solid #aaa;
    font-style: italic;
}
.tip-item {
    padding: 5px 0;
    font-size: 0.94rem;
}
.disclaimer {
    background: #f0f0f0;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #555;
    margin-top: 18px;
}
.gemini-badge {
    display: inline-block;
    background: linear-gradient(90deg, #4285F4, #EA4335, #FBBC05, #34A853);
    color: white;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-left: 8px;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    '## 🧠 Exam Anxiety Detector '
    '<span class="gemini-badge">✨ Powered by Gemini AI</span>',
    unsafe_allow_html=True,
)
st.markdown(
    "An intelligent mental-wellness support tool that uses **Google Gemini AI** "
    "to analyse your exam-related thoughts and provide **immediate, personalised guidance**."
)
st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# Input
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("📝 How are you feeling about your upcoming exam?")
user_text = st.text_area(
    label       = "Share your thoughts, feelings, or worries freely:",
    placeholder = "e.g. I'm completely overwhelmed and haven't slept in days because of this exam…",
    max_chars   = MAX_CHARS,
    height      = 150,
    key         = "user_input",
)

st.caption(f"{len(user_text)} / {MAX_CHARS} characters")

col1, col2 = st.columns([1, 3])
with col1:
    analyse_btn = st.button("🔍 Analyse", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state["user_input"] = ""
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# Analysis
# ──────────────────────────────────────────────────────────────────────────────
if analyse_btn:
    if not user_text.strip():
        st.warning("⚠️ Please enter some text before analysing.")
    else:
        with st.spinner("✨ Gemini AI is analysing your text…"):
            time.sleep(0.3)
            try:
                resp = requests.post(API_URL, json={"text": user_text}, timeout=30)
                resp.raise_for_status()
                data = resp.json()

                label      = data["label"]
                emoji      = data["emoji"]
                confidence = data["confidence"]
                tips       = data["tips"]
                probs      = data["probabilities"]
                reasoning  = data.get("reasoning", "")
                card_color = COLOR_HEX[label]
                card_bg    = BG_HEX[label]

                # ── Result card ──────────────────────────────────────────────
                st.markdown(
                    f"""
                    <div class="result-card"
                         style="background:{card_bg}; border-color:{card_color};">
                        <h2 style="color:{card_color}; margin:0 0 6px;">
                            {emoji} {label}
                        </h2>
                        <p style="margin:0; color:#444; font-size:0.95rem;">
                            Confidence: <strong>{confidence*100:.1f}%</strong>
                        </p>
                        {f'<div class="reasoning-box">💬 {reasoning}</div>' if reasoning else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("")  # spacer

                # ── Probability bars ─────────────────────────────────────────
                st.markdown("#### 📊 Anxiety Level Probabilities")
                for lbl, prob in probs.items():
                    c1, c2 = st.columns([2, 5])
                    with c1:
                        st.markdown(
                            f"<span style='color:{COLOR_HEX[lbl]};font-weight:600'>"
                            f"{EMOJIS_MAP.get(lbl,'')} {lbl}</span>",
                            unsafe_allow_html=True,
                        )
                    with c2:
                        st.progress(float(prob))
                        st.caption(f"{prob*100:.1f}%")

                # ── Tips ─────────────────────────────────────────────────────
                st.markdown(f"#### 💡 Personalised Tips for **{label}**")
                for tip in tips:
                    st.markdown(
                        f'<div class="tip-item">{tip}</div>',
                        unsafe_allow_html=True,
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to the backend API.\n\n"
                    "Start it in a separate terminal:\n\n"
                    "```bash\nuvicorn backend:app --host 0.0.0.0 --port 8000 --reload\n```"
                )
            except requests.exceptions.HTTPError as e:
                detail = ""
                try:
                    detail = e.response.json().get("detail", "")
                except Exception:
                    pass
                st.error(f"❌ API error: {detail or str(e)}")
            except Exception as exc:
                st.error(f"❌ Unexpected error: {exc}")


# ──────────────────────────────────────────────────────────────────────────────
# About & Disclaimer
# ──────────────────────────────────────────────────────────────────────────────
st.divider()

with st.expander("ℹ️ About this tool"):
    st.markdown("""
**Exam Anxiety Detector** uses **Google Gemini 1.5 Flash** — a state-of-the-art
large language model — to classify student-generated text into three anxiety levels:

| Level | Meaning |
|---|---|
| 😌 Low Anxiety | Mild stress; appears well-prepared |
| 😟 Moderate Anxiety | Noticeable stress; coping strategies advised |
| 😰 High Anxiety | Significant distress; professional support recommended |

**Architecture**
- *Frontend:* Streamlit
- *Backend:* FastAPI
- *AI Model:* Google Gemini 1.5 Flash via Gemini API
- *No local training needed* — Gemini understands anxiety language out of the box
    """)

st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> This tool is a <em>supportive, non-diagnostic</em>
instrument intended to raise self-awareness. It does <strong>not</strong> replace
professional psychological assessment or counselling. All text entries are processed
anonymously and are not stored. If you are in distress, please contact a qualified
mental-health professional or your institution's student-support service.
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📘 Use-Case Scenarios")

    st.markdown("### Scenario 1 – Student Self-Assessment")
    st.markdown(
        "Students enter their pre-exam thoughts. Gemini AI instantly "
        "classifies anxiety and provides calming, evidence-based tips."
    )

    st.markdown("### Scenario 2 – Institutional Monitoring")
    st.markdown(
        "Institutions aggregate anonymised trends to identify high-stress "
        "periods and proactively schedule counselling or workshops."
    )

    st.divider()
    st.markdown("**Tech Stack**")
    st.markdown("- ✨ Google Gemini 1.5 Flash")
    st.markdown("- ⚡ FastAPI")
    st.markdown("- 🎈 Streamlit")
    st.markdown("- 🐍 Python 3.9+")
    st.divider()
    st.markdown("🔑 [Get your free Gemini API key](https://aistudio.google.com/app/apikey)")
    st.caption("v2.0  •  Non-diagnostic supportive tool")
