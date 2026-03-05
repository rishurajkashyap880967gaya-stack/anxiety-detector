"""
app.py  –  Exam Anxiety Detector (Streamlit Cloud Edition)
           Gemini AI backend is embedded directly — no separate FastAPI server needed.
"""

import os
import json
import re

import streamlit as st
import google.generativeai as genai

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
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
TIPS = {
    "Low Anxiety": [
        "✅ Great – your stress level is manageable!",
        "💡 Keep up your steady study routine.",
        "🧘 A short mindfulness break can sharpen your focus.",
        "😴 Make sure you get a full night's sleep before the exam.",
        "🍎 Eat a nutritious meal to fuel your brain.",
    ],
    "Moderate Anxiety": [
        "🌬️ Try box breathing: inhale 4s → hold 4s → exhale 4s → hold 4s.",
        "📋 Break your revision into small, timed chunks (Pomodoro technique).",
        "🚶 A 10-minute walk can significantly lower cortisol levels.",
        "📖 Focus on topics you know well first to build confidence.",
        "💬 Talk to a friend, tutor, or counsellor about your worries.",
        "📵 Limit social media; it often amplifies pre-exam stress.",
    ],
    "High Anxiety": [
        "🆘 Your anxiety level is high – please reach out to a counsellor or trusted adult.",
        "🤝 You are NOT alone; many students feel this way and support is available.",
        "🛑 Stop cramming for now – rest is more valuable than extra study right now.",
        "📞 Contact your institution's student wellness / mental-health service.",
        "🧠 Remember: one exam does not define your worth or your future.",
        "🫁 Practice the 4-7-8 breathing technique to calm your nervous system.",
        "✍️ Write your fears on paper to externalise and reduce their power.",
    ],
}

SYSTEM_PROMPT = """
You are an expert educational psychologist specialising in student exam anxiety.
Analyse the student's text and classify their exam anxiety level.

Classify into EXACTLY one of:
  - Low Anxiety
  - Moderate Anxiety
  - High Anxiety

Definitions:
  Low Anxiety     : Mild nervousness, mostly calm, feels prepared.
  Moderate Anxiety: Noticeable stress, self-doubt, sleep issues, restlessness.
  High Anxiety    : Severe panic, overwhelming dread, physical symptoms, paralysis.

Respond ONLY with a valid JSON object — no markdown, no explanation:
{
  "label": "<Low Anxiety | Moderate Anxiety | High Anxiety>",
  "confidence": <float 0.0–1.0>,
  "probabilities": {
    "Low Anxiety": <float>,
    "Moderate Anxiety": <float>,
    "High Anxiety": <float>
  },
  "reasoning": "<one concise sentence explaining your classification>"
}

Rules:
- probabilities must sum to 1.0
- confidence must equal the highest probability
- label must match the highest probability category
"""


# ──────────────────────────────────────────────────────────────────────────────
# Gemini call
# ──────────────────────────────────────────────────────────────────────────────
def analyse_text(text: str, api_key: str) -> dict:
    genai.configure(api_key=api_key)
    model    = genai.GenerativeModel("gemini-1.5-flash")
    prompt   = f"{SYSTEM_PROMPT}\n\nStudent text:\n\"\"\"\n{text}\n\"\"\""
    response = model.generate_content(prompt)
    raw      = response.text.strip()

    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    result    = json.loads(raw)
    label     = result["label"]
    confidence= float(result["confidence"])
    probs     = {k: float(v) for k, v in result["probabilities"].items()}
    reasoning = result.get("reasoning", "")

    return {
        "label":         label,
        "confidence":    confidence,
        "probabilities": probs,
        "reasoning":     reasoning,
        "emoji":         EMOJIS_MAP[label],
        "tips":          TIPS[label],
    }


# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Exam Anxiety Detector · Gemini AI",
    page_icon  = "🧠",
    layout     = "centered",
)

st.markdown("""
<style>
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
.tip-item { padding: 5px 0; font-size: 0.94rem; }
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
    background: linear-gradient(90deg,#4285F4,#EA4335,#FBBC05,#34A853);
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
# API Key input (sidebar)
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔑 Gemini API Key")
    st.markdown(
        "Get your free key at "
        "[aistudio.google.com](https://aistudio.google.com/app/apikey)"
    )

    # Read from Streamlit secrets first (set in Streamlit Cloud dashboard)
    # Fall back to manual input
    secret_key = ""
    try:
        secret_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    if secret_key:
        api_key = secret_key
        st.success("✅ API key loaded from Secrets")
    else:
        api_key = st.text_input(
            "Paste your Gemini API key:",
            type="password",
            placeholder="AIzaSy...",
        )

    st.divider()
    st.markdown("**Use-Case Scenarios**")
    st.markdown("**Scenario 1 – Student Self-Assessment**")
    st.markdown("Enter your pre-exam thoughts; Gemini instantly classifies anxiety and gives tips.")
    st.markdown("**Scenario 2 – Institutional Monitoring**")
    st.markdown("Aggregate anonymised trends to identify high-stress periods.")
    st.divider()
    st.markdown("- ✨ Google Gemini 1.5 Flash")
    st.markdown("- 🎈 Streamlit Cloud")
    st.caption("v2.0  •  Non-diagnostic supportive tool")

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
    if not api_key:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar first.")
    elif not user_text.strip():
        st.warning("⚠️ Please enter some text before analysing.")
    else:
        with st.spinner("✨ Gemini AI is analysing your text…"):
            try:
                data       = analyse_text(user_text.strip(), api_key)
                label      = data["label"]
                emoji      = data["emoji"]
                confidence = data["confidence"]
                tips       = data["tips"]
                probs      = data["probabilities"]
                reasoning  = data.get("reasoning", "")
                card_color = COLOR_HEX[label]
                card_bg    = BG_HEX[label]

                # Result card
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

                st.markdown("")

                # Probability bars
                st.markdown("#### 📊 Anxiety Level Probabilities")
                for lbl, prob in probs.items():
                    c1, c2 = st.columns([2, 5])
                    with c1:
                        st.markdown(
                            f"<span style='color:{COLOR_HEX[lbl]};font-weight:600'>"
                            f"{EMOJIS_MAP[lbl]} {lbl}</span>",
                            unsafe_allow_html=True,
                        )
                    with c2:
                        st.progress(float(prob))
                        st.caption(f"{prob*100:.1f}%")

                # Tips
                st.markdown(f"#### 💡 Personalised Tips for **{label}**")
                for tip in tips:
                    st.markdown(f'<div class="tip-item">{tip}</div>', unsafe_allow_html=True)

            except json.JSONDecodeError:
                st.error("❌ Gemini returned an unexpected response. Please try again.")
            except Exception as exc:
                st.error(f"❌ Error: {exc}")

# ──────────────────────────────────────────────────────────────────────────────
# About & Disclaimer
# ──────────────────────────────────────────────────────────────────────────────
st.divider()

with st.expander("ℹ️ About this tool"):
    st.markdown("""
**Exam Anxiety Detector** uses **Google Gemini 1.5 Flash** to classify student
text into three anxiety levels:

| Level | Meaning |
|---|---|
| 😌 Low Anxiety | Mild stress; appears well-prepared |
| 😟 Moderate Anxiety | Noticeable stress; coping strategies advised |
| 😰 High Anxiety | Significant distress; professional support recommended |

**Architecture:** Streamlit + Google Gemini API (single-file deployment)
    """)

st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> This tool is a <em>supportive, non-diagnostic</em>
instrument. It does <strong>not</strong> replace professional psychological assessment
or counselling. All text is processed anonymously and never stored. If you are in
distress, please contact a qualified mental-health professional.
</div>
""", unsafe_allow_html=True)
