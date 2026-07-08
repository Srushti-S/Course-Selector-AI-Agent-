"""
Main FastAPI Application — AI Course Planner v2
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
import os
from dotenv import load_dotenv

from app.models import StudentProfile, RecommendationResponse, PlanResponse
from app.services import CourseRecommendationService, parse_prereqs
from app.data import COURSE_CATALOG

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Course Planner API",
    description="Backend for personalized course recommendations",
    version="2.1.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommendation_service = CourseRecommendationService()


@app.get("/")
async def root():
    return {
        "message": "AI Course Planner API",
        "version": "2.1.0",
        "status": "running",
        "ai_enabled": recommendation_service.ai_enabled,
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "ai_enabled": recommendation_service.ai_enabled}


@app.post("/api/recommendations", response_model=RecommendationResponse)
async def get_recommendations(profile: StudentProfile):
    try:
        source, recommendations = recommendation_service.generate_recommendations(
            profile=profile, course_catalog=COURSE_CATALOG
        )
        return RecommendationResponse(source=source, recommendations=recommendations)
    except Exception:
        logger.exception("Recommendation generation failed")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@app.post("/api/plan", response_model=PlanResponse)
async def generate_plan(profile: StudentProfile):
    try:
        source, plan = recommendation_service.generate_semester_plan(
            profile=profile, course_catalog=COURSE_CATALOG
        )
        return PlanResponse(source=source, plan=plan)
    except Exception:
        logger.exception("Plan generation failed")
        raise HTTPException(status_code=500, detail="Failed to generate semester plan")


@app.get("/api/courses")
async def get_courses(
    major: Optional[str] = Query(None),
    level: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
):
    results = COURSE_CATALOG
    if major:
        results = [c for c in results if c["major"].lower() == major.lower()]
    if level:
        results = [c for c in results if c["level"] == level]
    if search:
        q = search.lower()
        results = [
            c for c in results
            if q in c["code"].lower() or q in c["name"].lower() or q in c.get("description", "").lower()
        ]
    return {"total": len(results), "courses": results}


@app.get("/api/courses/{code}")
async def get_course(code: str):
    course = next((c for c in COURSE_CATALOG if c["code"] == code), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@app.get("/api/majors")
async def get_majors():
    return {
        "majors": [
            "Computer Science", "Data Science", "Software Engineering",
            "Information Systems", "Cybersecurity", "Artificial Intelligence",
        ]
    }


@app.get("/api/prerequisites/{code}")
async def get_prerequisites(code: str):
    target = next((c for c in COURSE_CATALOG if c["code"] == code), None)
    if not target:
        raise HTTPException(status_code=404, detail="Course not found")

    def get_chain(course_code, visited):
        if course_code in visited:
            return []
        visited.add(course_code)
        course = next((c for c in COURSE_CATALOG if c["code"] == course_code), None)
        if not course:
            return []
        chain = []
        for pc in parse_prereqs(course.get("prerequisites", "None")):
            chain.extend(get_chain(pc, visited))
        chain.append(course)
        return chain

    return {"course": code, "chain": get_chain(code, set())}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
