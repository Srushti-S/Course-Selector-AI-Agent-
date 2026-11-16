# ● Course Planner — AI-Powered Academic Planning

![CI](https://github.com/Srushti-S/Course-Selector-AI-Agent-/actions/workflows/ci.yml/badge.svg) ![Tech Stack](https://img.shields.io/badge/React-18-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal) ![LangChain](https://img.shields.io/badge/LangChain-AI-orange)

A course recommendation and academic planning system. Students describe their major, completed courses, interests, and career goals; the app recommends courses, builds a full multi-semester schedule, and visualizes the prerequisite graph. LLM output is never trusted blindly — every AI response is validated server-side against the catalog, prerequisites, and credit limits, and a deterministic engine serves identical features when the API is unavailable.

## Live Demo

- **App:** https://course-planner-frontend.onrender.com
- **API docs (Swagger):** https://course-planner-api.onrender.com/docs

Hosted on Render's free tier — the first request after idle can take up to a minute to wake the backend.

## Features

- **AI-Powered Recommendations** — LangChain + OpenAI with structured outputs (typed Pydantic schemas, no JSON string parsing). Falls back to a deterministic rule-based engine when no API key is set or the API is unavailable, and every response reports its `source` (`ai` or `rules`).
- **Semantic Interest Matching** — Course descriptions are embedded with `text-embedding-3-small` and ranked by cosine similarity against the student's interests and career goals, with keyword matching as the offline fallback.
- **LLM-Generated Semester Plans** — One click builds a full 4-semester schedule. Every AI plan is validated server-side: unknown courses dropped, prerequisite order enforced, credit caps respected. The deterministic planner takes over if the model fails.
- **Drag-and-Drop Planner** — Move courses between semesters; prerequisite and credit-limit checks run in the browser, so conflicts are flagged the moment a card lands.
- **Prerequisite Map** — The 42-course catalog rendered by level, showing completed / available / locked status per course, with a detail panel for dependency chains.
- **Saved Plans** — Plans persist to SQLite and get a shareable link (`?plan=<id>`).

## How It Works

1. The React app posts a `StudentProfile` to `/api/recommendations` or `/api/plan`.
2. If an OpenAI key is configured, a LangChain chain (`gpt-4o-mini`, temperature 0) returns a typed response via `with_structured_output`, parsed straight into a Pydantic schema.
3. The service validates every item against the catalog: hallucinated course codes are dropped, priorities normalized, plan semesters checked for prerequisite ordering and credit caps.
4. If the model is unavailable, times out, or returns an unusable result, the same request is served by a deterministic scorer that weighs major fit, course level vs. student year, interest similarity, and prerequisite completion.
5. Interest similarity uses cached OpenAI embeddings of the catalog; without a key it degrades to keyword matching.
6. The offline eval harness scores both paths across 24 synthetic student profiles so regressions show up as numbers, not vibes.

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

Add a real `OPENAI_API_KEY` to `.env` to enable the AI path; without one the deterministic engine serves all requests.

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

### Evals

The engine is scored offline against 24 synthetic student profiles (every major × year combination). The harness checks that generated plans never violate prerequisites, measures how full each semester is, and tracks how well recommendations line up with stated interests.

```bash
cd backend
python evals.py
```

```
profiles evaluated:      24
planner source(s):       rules
prereq violations:       0
avg credit utilization:  98%
avg courses per plan:    19.5
interest match rate:     5%
avg plan latency:        0.2 ms
```

The low interest match rate on the keyword fallback is what motivated the embedding-based matching — re-run with an `OPENAI_API_KEY` set to compare.

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
| `POST` | `/api/plans` | Save a plan → `{id}` |
| `GET` | `/api/plans/{id}` | Load a saved plan |

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
    db.py          ← SQLite persistence for saved plans
  tests/           ← API tests (pytest + TestClient)
  evals.py         ← Offline scoring across synthetic profiles
```

## Tech Stack

**Frontend:** React 18, CSS custom properties (light theme), Plus Jakarta Sans + Fira Code  
**Backend:** Python 3.10+, FastAPI, Pydantic v2, LangChain (`langchain-core` + `langchain-openai`), OpenAI, SQLite
