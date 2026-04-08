"""
Pydantic Models — Enhanced
"""
from pydantic import BaseModel
from typing import List, Optional


class StudentProfile(BaseModel):
    name: str
    major: str
    year: str
    completedCourses: List[str] = []
    interests: List[str] = []
    careerGoals: str
    creditHoursPerSemester: int = 15

    class Config:
        json_schema_extra = {
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


class Recommendation(BaseModel):
    id: int
    courseCode: str
    courseName: str
    credits: int
    semester: str
    reason: str
    priority: str  # high, medium, low
    prerequisites: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    major: Optional[str] = None


class SemesterPlan(BaseModel):
    semester: str
    courses: List[Recommendation]
    totalCredits: int


class CourseDetail(BaseModel):
    code: str
    name: str
    credits: int
    level: int
    major: str
    prerequisites: str
    description: str
