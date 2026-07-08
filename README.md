# ● Course Planner — AI-Powered Academic Planning

An intelligent course recommendation and academic planning system built with **React**, **FastAPI**, and **LangChain**.

![Tech Stack](https://img.shields.io/badge/React-18-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal) ![LangChain](https://img.shields.io/badge/LangChain-AI-orange)

## Features

- **AI-Powered Recommendations** — Uses LangChain + OpenAI to generate personalized course suggestions based on your profile, interests, and career goals. Falls back gracefully to a deterministic rule-based engine when no API key is set or the API is unavailable, and every response reports its `source` (`ai` or `rules`).
- **LLM-Generated Semester Plans** — One click in the Planner tab asks the LLM to build a full 4-semester schedule; every AI plan is validated server-side against prerequisites and credit limits, with the deterministic planner as fallback.
- **Dynamic Prerequisite Map** — Visualize the entire course catalog as an interactive prerequisite map. Filter by major, see what's completed/available/locked, and click any course to explore its dependency chain.
- **Drag-and-Drop Planner** — Move courses between semesters with credit limit warnings and overload detection; prerequisite and credit checks run in the browser.
- **Smart Profile Builder** — Searchable course catalog for completed courses, clickable interest tags, and structured career goal input.
- **Course Catalog API** — 42 courses, filterable by major, level, or search query.
- **Prerequisite Chain API** — Get the full dependency tree for any course.

## Quick Start

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Add a real `OPENAI_API_KEY` to `.env` to enable AI recommendations; without one the deterministic engine serves all requests.

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs on `http://localhost:3000` and targets the backend at `http://localhost:8000` by default. Set `REACT_APP_API_URL` at build time to point elsewhere.

### Tests

```bash
cd backend
pytest
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check + AI status |
| `POST` | `/api/recommendations` | Get course recommendations → `{source, recommendations}` |
| `POST` | `/api/plan` | Generate multi-semester plan → `{source, plan}` |
| `GET` | `/api/courses?major=&level=&search=` | Browse/filter course catalog |
| `GET` | `/api/courses/{code}` | Get single course details |
| `GET` | `/api/prerequisites/{code}` | Get prerequisite chain |
| `GET` | `/api/majors` | List available majors |

## Architecture

```
frontend/          React 18 SPA
  src/
    components/
      StudentProfile.jsx        ← Profile form with catalog search
      RecommendationPanel.jsx   ← AI recommendation cards
      CoursePlanner.jsx         ← Drag-and-drop semester planner
      PrerequisiteVisualization.jsx ← Dynamic prereq map

backend/           FastAPI + LangChain
  app/
    main.py        ← API routes
    models.py      ← Pydantic schemas
    services.py    ← Recommendation + planning engine (AI + fallback)
    data.py        ← Course catalog (42 courses)
  tests/           ← API tests (pytest + TestClient)
```

## Tech Stack

**Frontend:** React 18, CSS custom properties (dark theme), DM Sans + JetBrains Mono  
**Backend:** Python 3.10+, FastAPI, Pydantic v2, LangChain (`langchain-core` + `langchain-openai`), OpenAI
