"""
backend.py  –  FastAPI inference server using Google Gemini AI
               for the Exam Anxiety Detector.

Endpoints
---------
GET  /          → health check
POST /predict   → { "text": "..." }  →  anxiety prediction + tips

Run
---
    uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import json
import re
from dotenv import load_dotenv

import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# Gemini setup
# ──────────────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY not set. "
        "Copy .env.example → .env and add your key from "
        "https://aistudio.google.com/app/apikey"
    )

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# ──────────────────────────────────────────────────────────────────────────────
# Static resources
# ──────────────────────────────────────────────────────────────────────────────
TIPS = {
    "Low Anxiety": [
        "✅ Great – your stress level is manageable!",
        "💡 Keep up your steady study routine.",
        "🧘 A short mindfulness break can sharpen your focus.",
        "😴 Make sure you get a full night's sleep before the exam.",
        "🍎 Eat a nutritious meal to fuel your brain.",
    ],
    "Moderate Anxiety": [
        "🌬️ Try box breathing: inhale 4 s → hold 4 s → exhale 4 s → hold 4 s.",
        "📋 Break your revision into small, timed chunks (Pomodoro technique).",
        "🚶 A 10-minute walk can significantly lower cortisol levels.",
        "📖 Focus on topics you know well first to build confidence.",
        "💬 Talk to a friend, tutor, or counsellor about your worries.",
        "📵 Limit social media; it often amplifies pre-exam comparison stress.",
    ],
    "High Anxiety": [
        "🆘 Your anxiety level is high – please reach out to a counsellor or trusted adult.",
        "🤝 You are NOT alone; many students feel this way and support is available.",
        "🛑 Stop cramming for now – rest is more valuable than additional study right now.",
        "📞 Contact your institution's student wellness / mental-health service.",
        "🧠 Remember: one exam does not define your worth or your future.",
        "🫁 Practice the 4-7-8 breathing technique to calm your nervous system.",
        "✍️ Write your fears on paper to externalise and reduce their power.",
    ],
}

EMOJIS = {
    "Low Anxiety":      "😌",
    "Moderate Anxiety": "😟",
    "High Anxiety":     "😰",
}

COLORS = {
    "Low Anxiety":      "green",
    "Moderate Anxiety": "orange",
    "High Anxiety":     "red",
}


# ──────────────────────────────────────────────────────────────────────────────
# Gemini prompt
# ──────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert educational psychologist specialising in student exam anxiety.
Your task is to analyse a student's text and classify their exam anxiety level.

Classify into EXACTLY one of these three categories:
  - Low Anxiety
  - Moderate Anxiety
  - High Anxiety

Definitions:
  Low Anxiety     : Mild nervousness, mostly calm, feels prepared.
  Moderate Anxiety: Noticeable stress, some self-doubt, sleep issues, restlessness.
  High Anxiety    : Severe panic, overwhelming dread, physical symptoms, paralysis.

You MUST respond with ONLY a valid JSON object — no markdown, no explanation:
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
- confidence must equal the highest probability value
- label must match the category with the highest probability
"""


def call_gemini(text: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\n\nStudent text:\n\"\"\"\n{text}\n\"\"\""
    response = gemini_model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown code fences if Gemini wraps in ```json ... ```
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


def predict_anxiety(text: str) -> dict:
    result    = call_gemini(text)
    label     = result["label"]
    confidence= float(result["confidence"])
    probs     = {k: float(v) for k, v in result["probabilities"].items()}
    reasoning = result.get("reasoning", "")

    return {
        "label":         label,
        "label_index":   ["Low Anxiety", "Moderate Anxiety", "High Anxiety"].index(label),
        "confidence":    confidence,
        "probabilities": probs,
        "reasoning":     reasoning,
        "emoji":         EMOJIS[label],
        "color":         COLORS[label],
        "tips":          TIPS[label],
    }


# ──────────────────────────────────────────────────────────────────────────────
# FastAPI app
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Exam Anxiety Detector API (Gemini AI)",
    description = "NLP-powered anxiety classification using Google Gemini. "
                  "⚠️ Supportive tool only — NOT a clinical diagnostic instrument.",
    version     = "2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    text: str


class PredictResponse(BaseModel):
    label:         str
    label_index:   int
    confidence:    float
    probabilities: dict
    reasoning:     str
    emoji:         str
    color:         str
    tips:          list


@app.get("/")
def health():
    return {
        "status":     "ok",
        "service":    "Exam Anxiety Detector",
        "ai_backend": "Google Gemini 1.5 Flash",
        "disclaimer": "Non-diagnostic supportive tool only.",
    }


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Input text cannot be empty.")
    if len(text) > 2000:
        raise HTTPException(status_code=422, detail="Input exceeds 2 000 character limit.")

    try:
        result = predict_anxiety(text)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"Gemini returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

    return result
