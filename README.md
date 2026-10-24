# DermaLens — AI-Assisted Skin Condition Screening

An end-to-end web app that classifies skin conditions from an uploaded
photo using a fine-tuned MobileNetV2 CNN, explains its prediction with
a Grad-CAM heatmap, and gives the user simple next-step guidance.

This is the **buildable v1 scope**, trimmed down from the original
project report to something one person (or a small team) can actually
finish and demo in 6-8 weeks. See "Full vision vs. this build" below.
Digital Twin Challenge | Healthcare AI | Machine Learning

# Team Details

**Team Member:** Anvesha Singh

**Institution:** Pranveer Singh Institute of Technology (PSIT), Kanpur, UttarPradesh, India

Course: Bachelor of Technology (B.Tech)

Year of Study: 3rd Year

Department: Computer Science and Engineering (CSE)

# College / Incubator Information

Institution: Pranveer Singh Institute of Technology (PSIT)

Location: Kanpur, Uttar Pradesh, India

Academic Program: B.Tech in Computer Science and Engineering


## Problem Statement

Skin conditions can be difficult for individuals to assess without professional guidance.
 Access to dermatologists may be limited by geographical barriers, waiting times, cost, and a lack of awareness.

Existing image-classification systems may also provide predictions without explaining which image regions influenced 
their outputs.

DermaLens addresses these challenges by developing a web-based screening aid that combines image classification, visual 
explainability, and simple next-step guidance.

The system is intended for preliminary screening and educational demonstration, not for diagnosing diseases or 
replacing qualified healthcare professionals.

## Stack

- **Model:** TensorFlow/Keras, MobileNetV2 transfer learning, Grad-CAM
- **Backend:** FastAPI, SQLAlchemy, SQLite (swap for Postgres in prod),
  JWT auth
- **Frontend:** React (Vite), Tailwind CSS, React Router
S
## Project structure

```
dermalens/
  model/          training pipeline (run locally / on Colab with a GPU)
    dataset_prep.py   organizes raw downloaded images into train/val/test
    train.py           trains MobileNetV2, saves dermalens_model.h5
    gradcam.py          Grad-CAM heatmap generation, used by the backend
  backend/        FastAPI service
    main.py
    routers/        auth.py, analyze.py, history.py
    models/schemas.py  SQLAlchemy tables + Pydantic schemas
  frontend/       React app
    src/pages/       Home, Login, Signup, Upload, Dashboard
```

## 1. Get a dataset

See `model/dataset_prep.py` for full details and links. Short version:
download the **"Human Skin Diseases (Image)"** Kaggle dataset (has Acne
and Tinea/fungal classes) and optionally combine with the
**"Skin diseases image dataset"** (ismailpromus) for more volume. Put
the raw folders under `model/data/raw/`, edit `CLASS_MAP` in
`dataset_prep.py` to match the actual folder names you get, then run:

```bash
cd model
pip install -r requirements.txt
python dataset_prep.py
```

This produces `model/data/train`, `val`, `test` folders per class.

## 2. Train the model

```bash
cd model
python train.py
```

Runs on CPU but is much faster with a GPU — Google Colab (free tier) is
a good option if your laptop doesn't have one. Produces
`dermalens_model.h5` and `class_names.json`.

## 3. Run the backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # edit values if needed
uvicorn main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`.

## 4. Run the frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App at `http://localhost:5173`.

## Full vision vs. this build

The original report scoped a much larger platform: dual backend
(Node+Express *and* FastAPI), symptom questionnaires, real
teleconsultation booking with licensed dermatologists, severity
grading, GDPR-grade compliance, and multi-platform (mobile) apps.

This build keeps the technically substantial, honestly-deliverable
core — CNN classification, explainability, a working full-stack app,
cloud deployment — and treats the rest as **documented future
roadmap** rather than half-built features. On a resume/in an
interview, this is a stronger story: "I scoped a large system, shipped
a working core, and can articulate exactly what I'd build next and
why" beats a bigger feature list that doesn't actually run.

### Roadmap (not yet built)
- Severity scoring per condition (needs richer labels than most public
  datasets provide)
- Real teleconsultation booking (needs an actual provider integration)
- Native mobile apps
- Multi-condition detection (currently single-label classification)

## Deployment (once trained + working locally)

- **Frontend:** Vercel (`vercel deploy` from `frontend/`)
- **Backend:** Render or Railway — note the model file is ~10-15MB,
  fine for these platforms' free tiers
- **Database:** swap SQLite for Postgres (Render/Railway/Supabase all
  offer free Postgres) by changing `DATABASE_URL` in `.env`

## Important note on framing

Be upfront in your README/demo/interview that this is a **screening
aid, not a diagnostic tool**, trained on a limited public dataset. That
honesty is a plus, not a minus — it shows you understand the
real-world stakes of applying ML to health data.
