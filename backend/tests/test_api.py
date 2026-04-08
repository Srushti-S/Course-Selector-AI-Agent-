"""
API Tests
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import StudentProfile
from app.services import CourseRecommendationService
from app.data import COURSE_CATALOG


def test_generate_recommendations():
    """Test recommendation generation"""
    
    profile = StudentProfile(
        name="Alice Johnson",
        major="Computer Science",
        year="Sophomore",
        completedCourses=["CS101", "MATH201"],
        interests=["Machine Learning", "Web Development"],
        careerGoals="Become a full-stack developer",
        creditHoursPerSemester=15
    )
    
    service = CourseRecommendationService()
    recommendations = service.generate_recommendations(profile, COURSE_CATALOG)
    
    assert len(recommendations) > 0
    assert all(rec.courseCode not in profile.completedCourses for rec in recommendations)
    print(f"✅ Generated {len(recommendations)} recommendations")
    
    for rec in recommendations[:3]:
        print(f"  - {rec.courseCode}: {rec.courseName} ({rec.priority})")


if __name__ == '__main__':
    test_generate_recommendations()
    print("\n✅ All tests passed!")