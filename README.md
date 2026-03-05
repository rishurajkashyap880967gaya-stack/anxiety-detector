# 🧠 Exam Anxiety Detector — Gemini AI Edition

> An intelligent mental-wellness support system powered by **Google Gemini 1.5 Flash** that classifies student exam-related text into **Low**, **Moderate**, and **High** anxiety levels with personalised coping tips.

---

## ✨ What Changed from BERT Version

| Feature | BERT Version | Gemini AI Version |
|---|---|---|
| AI Model | Fine-tuned BERT (local) | Google Gemini 1.5 Flash (API) |
| Training required | Yes (~20 min) | ❌ No training needed |
| Local GPU/CPU load | High | None |
| Setup time | 30–60 min | ~5 min |
| Reasoning output | No | ✅ Yes — Gemini explains its classification |
| Internet required | First download only | Yes (API calls) |
| API Key needed | No | ✅ Yes (free) |

---

## Architecture

```
┌─────────────────────────────────────┐
│         Presentation Layer          │  ← Streamlit (app.py)
└──────────────┬──────────────────────┘
               │ HTTP POST /predict
┌──────────────▼──────────────────────┐
│         Application Layer           │
│  ┌──────────────────────────────┐   │
│  │  FastAPI backend (backend.py)│   │
│  │  ↓                           │   │
│  │  Gemini 1.5 Flash API call   │   │  ← Google Gemini API
│  │  ↓                           │   │
│  │  JSON parse → tips + emoji   │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Project Structure

```
exam_anxiety_detector/
├── app.py               # Streamlit frontend
├── backend.py           # FastAPI server with Gemini AI
├── requirements.txt     # Python dependencies
├── .env.example         # API key template
├── .env                 # Your actual API key (you create this)
└── README.md
```

---

## Quick Start

### Step 1 — Get a Free Gemini API Key

1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key

---

### Step 2 — Set Up the Environment

```bash
# Python 3.9+ required
python3 -m venv venv

# Activate
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate.bat         # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3 — Configure Your API Key

```bash
# Copy the template
cp .env.example .env

# Open .env and paste your key
# GEMINI_API_KEY=AIzaSy...your_key_here
```

Or on Linux/macOS in one line:
```bash
echo "GEMINI_API_KEY=your_key_here" > .env
```

---

### Step 4 — Start the FastAPI Backend

```bash
uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

Test it:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I am terrified and cannot sleep because of the exam."}'
```

Interactive docs → **http://localhost:8000/docs**

---

### Step 5 — Launch the Streamlit Frontend

Open a **new terminal**, activate venv, then:

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## API Reference

### `POST /predict`

**Request**
```json
{ "text": "I feel calm and well prepared for the exam tomorrow." }
```

**Response**
```json
{
  "label":        "Low Anxiety",
  "label_index":  0,
  "confidence":   0.88,
  "probabilities": {
    "Low Anxiety":      0.88,
    "Moderate Anxiety": 0.09,
    "High Anxiety":     0.03
  },
  "reasoning": "The student expresses calmness and confidence in their preparation.",
  "emoji":  "😌",
  "color":  "green",
  "tips":   ["✅ Great – your stress level is manageable!", "..."]
}
```

---

## Anxiety Categories

| Level | Index | Indicator |
|---|---|---|
| 😌 Low Anxiety | 0 | Mild stress; well-prepared |
| 😟 Moderate Anxiety | 1 | Noticeable stress; coping strategies advised |
| 😰 High Anxiety | 2 | Significant distress; professional support recommended |

---

## Requirements

```
google-generativeai==0.7.2
fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.1
requests==2.31.0
pydantic==2.4.2
python-dotenv==1.0.0
```

---

## Disclaimer

> ⚠️ This system is a **supportive, non-diagnostic** tool. It does **not** replace professional psychological assessment. All inputs are processed anonymously. If experiencing severe distress, please contact a mental-health professional.
