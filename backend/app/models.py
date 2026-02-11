"""
Pydantic Models - Match Frontend Data Structure
"""
from pydantic import BaseModel
from typing import List, Optional


class StudentProfile(BaseModel):
    """
    Student profile - matches frontend studentProfile state exactly
    """
    name: str
    major: str
    year: str  # Freshman, Sophomore, Junior, Senior
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
                "creditHoursPerSemester": 15
            }
        }


class Recommendation(BaseModel):
    """
    Course recommendation - matches frontend recommendations array structure
    """
    id: int
    courseCode: str
    courseName: str
    credits: int
    semester: str
    reason: str
    priority: str  # 'high', 'medium', 'low'
    prerequisites: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "courseCode": "CS201",
                "courseName": "Data Structures",
                "credits": 3,
                "semester": "Fall 2024",
                "reason": "Core Computer Science course",
                "priority": "high",
                "prerequisites": "CS101"
            }
        }