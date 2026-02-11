"""
Main FastAPI Application
Perfectly matched to the frontend API calls
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from dotenv import load_dotenv

from app.models import StudentProfile, Recommendation
from app.services import CourseRecommendationService
from app.data import COURSE_CATALOG

# Load environment
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="AI Course Planner API",
    description="Backend for personalized course recommendations",
    version="1.0.0"
)

# CORS - Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",  # ADD THIS LINE
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"   # ADD THIS LINE
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize service
recommendation_service = CourseRecommendationService()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Course Planner API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/api/recommendations", response_model=List[Recommendation])
async def get_recommendations(profile: StudentProfile):
    """
    Generate AI-powered course recommendations
    This matches the frontend's handleGetRecommendations function
    """
    try:
        recommendations = recommendation_service.generate_recommendations(
            profile=profile,
            course_catalog=COURSE_CATALOG
        )
        return recommendations
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses")
async def get_courses():
    """Get all available courses"""
    return {
        "total": len(COURSE_CATALOG),
        "courses": COURSE_CATALOG
    }


@app.get("/api/majors")
async def get_majors():
    """Get available majors"""
    majors = [
        'Computer Science',
        'Data Science',
        'Software Engineering',
        'Information Systems',
        'Cybersecurity',
        'Artificial Intelligence'
    ]
    return {"majors": majors}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)