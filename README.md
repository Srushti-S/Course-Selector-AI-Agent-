# 🎓 AI Course Planner

AI-powered course recommendation and academic planning system.

## Project Structure

```
├── frontend/          # React frontend
├── backend/           # Python backend (FastAPI + LangChain)
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## Quick Start

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Features

- 🤖 AI-powered course recommendations using LangChain
- ✅ Prerequisite validation engine
- 📊 Course schedule optimization
- 🎯 Personalized academic planning
- 📈 Progress tracking and visualization

## Tech Stack

**Frontend:** React, Modern CSS
**Backend:** Python, FastAPI, LangChain, OpenAI
**Testing:** Pytest, Jest

## Documentation

- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Strategy](docs/TESTING.md)

## License

MIT License
