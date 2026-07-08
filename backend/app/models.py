"""
Pydantic Models — Enhanced
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class StudentProfile(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    major: str = Field(min_length=1, max_length=100)
    year: str = Field(min_length=1, max_length=30)
    completedCourses: List[str] = []
    interests: List[str] = []
    careerGoals: str = Field(min_length=1, max_length=2000)
    creditHoursPerSemester: int = Field(default=15, ge=3, le=30)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Alice Johnson",
                "major": "Computer Science",
                "year": "Sophomore",
                "completedCourses": ["CS101", "MATH201"],
                "interests": ["Machine Learning", "Web Development"],
                "careerGoals": "Become a full-stack developer",
                "creditHoursPerSemester": 15,
            }
        }
    }


class Recommendation(BaseModel):
    id: int
    courseCode: str
    courseName: str
    credits: int
    semester: str
    reason: str
    priority: str
    prerequisites: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    major: Optional[str] = None


class RecommendationResponse(BaseModel):
    source: str
    recommendations: List[Recommendation]


class SemesterPlan(BaseModel):
    semester: str
    courses: List[Recommendation]
    totalCredits: int


class PlanResponse(BaseModel):
    source: str
    plan: List[SemesterPlan]


class CourseDetail(BaseModel):
    code: str
    name: str
    credits: int
    level: int
    major: str
    prerequisites: str
    description: str
