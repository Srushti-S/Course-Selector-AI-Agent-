"""
Main FastAPI Application — AI Course Planner v2
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import re
from dotenv import load_dotenv

from app.models import StudentProfile, Recommendation, SemesterPlan, CourseDetail
from app.services import CourseRecommendationService
from app.data import COURSE_CATALOG

load_dotenv()

app = FastAPI(
    title="AI Course Planner API",
    description="Backend for personalized course recommendations",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommendation_service = CourseRecommendationService()


@app.get("/")
async def root():
    return {
        "message": "AI Course Planner API",
        "version": "2.0.0",
        "status": "running",
        "ai_enabled": recommendation_service.ai_enabled,
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "ai_enabled": recommendation_service.ai_enabled}


@app.post("/api/recommendations", response_model=List[Recommendation])
async def get_recommendations(profile: StudentProfile):
    try:
        return recommendation_service.generate_recommendations(
            profile=profile, course_catalog=COURSE_CATALOG
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/plan", response_model=List[SemesterPlan])
async def generate_plan(profile: StudentProfile):
    try:
        return recommendation_service.generate_semester_plan(
            profile=profile, course_catalog=COURSE_CATALOG
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    def get_chain(course_code, visited=None):
        if visited is None:
            visited = set()
        if course_code in visited:
            return []
        visited.add(course_code)
        course = next((c for c in COURSE_CATALOG if c["code"] == course_code), None)
        if not course:
            return []
        prereq_str = course.get("prerequisites", "None")
        if prereq_str == "None":
            return [course]
        codes = re.findall(r"[A-Z]{2,4}\d{3}", prereq_str)
        chain = []
        for pc in codes:
            chain.extend(get_chain(pc, visited))
        chain.append(course)
        return chain

    return {"course": code, "chain": get_chain(code)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
