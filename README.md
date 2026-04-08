# ● Course Planner — AI-Powered Academic Planning

An intelligent course recommendation and academic planning system built with **React**, **FastAPI**, and **LangChain**.

![Tech Stack](https://img.shields.io/badge/React-18-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal) ![LangChain](https://img.shields.io/badge/LangChain-AI-orange)

## Features

- **AI-Powered Recommendations** — Uses LangChain + OpenAI to generate personalized course suggestions based on your profile, interests, and career goals. Falls back gracefully to a smart rule-based engine when no API key is set.
- **Dynamic Prerequisite Map** — Visualize the entire course catalog as an interactive prerequisite graph. Filter by major, see what's completed/available/locked, and click any course to explore its dependency chain.
- **Semester Planner** — Drag-and-drop courses between semesters with credit limit warnings and overload detection.
- **Smart Profile Builder** — Searchable course catalog for completed courses (no more guessing course codes), clickable interest tags, and structured career goal input.
- **Multi-Semester Plan Generation** — Backend `/api/plan` endpoint builds a full 4-semester plan respecting prerequisites and credit limits.
- **Course Catalog API** — Filterable by major, level, or search query.
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

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs on `http://localhost:3000` and expects the backend at `http://localhost:8000`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check + AI status |
| `POST` | `/api/recommendations` | Get AI course recommendations |
| `POST` | `/api/plan` | Generate multi-semester plan |
| `GET` | `/api/courses?major=&level=&search=` | Browse/filter course catalog |
| `GET` | `/api/courses/{code}` | Get single course details |
| `GET` | `/api/prerequisites/{code}` | Get prerequisite chain |
| `GET` | `/api/majors` | List available majors |

## Architecture

```
frontend/          React 18 SPA
  src/
    components/
      StudentProfile.jsx       ← Profile form with catalog search
      RecommendationPanel.jsx   ← AI recommendation cards
      CoursePlanner.jsx         ← Drag-and-drop semester planner
      PrerequisiteVisualization.jsx ← Dynamic prereq map

backend/           FastAPI + LangChain
  app/
    main.py        ← API routes
    models.py      ← Pydantic schemas
    services.py    ← Recommendation engine (AI + fallback)
    data.py        ← Course catalog (36 courses)
```

## Tech Stack

**Frontend:** React 18, CSS custom properties (dark theme), DM Sans + JetBrains Mono  
**Backend:** Python 3.10+, FastAPI, Pydantic v2, LangChain, OpenAI  
**Design:** Dark editorial UI, amber accent system, responsive grid layout

## License

MIT
