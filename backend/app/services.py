"""
Course Recommendation Service
Generates personalized recommendations based on student profile
"""
from typing import List
import re
from app.models import StudentProfile, Recommendation


class CourseRecommendationService:
    """Service for generating course recommendations"""
    
    def generate_recommendations(
        self, 
        profile: StudentProfile, 
        course_catalog: List[dict]
    ) -> List[Recommendation]:
        """
        Generate personalized course recommendations
        
        Args:
            profile: Student profile from frontend
            course_catalog: Available courses
            
        Returns:
            List of Recommendation objects matching frontend structure
        """
        
        # Filter out already completed courses
        completed = set(profile.completedCourses)
        available = [c for c in course_catalog if c['code'] not in completed]
        
        # Score and rank courses
        scored_courses = self._score_courses(profile, available)
        
        # Generate recommendations
        recommendations = []
        for i, item in enumerate(scored_courses[:8], start=1):
            course = item['course']
            score = item['score']
            reasons = item['reasons']
            
            # Determine priority based on score
            if score >= 8:
                priority = 'high'
            elif score >= 5:
                priority = 'medium'
            else:
                priority = 'low'
            
            # Build reason string
            reason = '; '.join(reasons) if reasons else "Recommended for your program"
            
            # Alternate semesters
            semester = "Fall 2024" if i % 2 == 1 else "Spring 2025"
            
            recommendations.append(
                Recommendation(
                    id=i,
                    courseCode=course['code'],
                    courseName=course['name'],
                    credits=course['credits'],
                    semester=semester,
                    reason=reason,
                    priority=priority,
                    prerequisites=course.get('prerequisites', 'None')
                )
            )
        
        return recommendations
    
    def _score_courses(self, profile: StudentProfile, available: List[dict]) -> List[dict]:
        """Score courses based on relevance to student profile"""
        
        year_to_level = {
            'Freshman': 1,
            'Sophomore': 2,
            'Junior': 3,
            'Senior': 4
        }
        current_level = year_to_level.get(profile.year, 2)
        
        scored = []
        for course in available:
            score = 0
            reasons = []
            
            # 1. Major alignment (highest priority)
            major_code = profile.major.split()[0]  # "Computer Science" -> "Computer"
            if major_code.upper()[:2] in course['code']:
                score += 5
                reasons.append(f"Core {profile.major} course")
            
            # 2. Level appropriateness
            if course['level'] == current_level:
                score += 3
                reasons.append(f"Perfect level for {profile.year}")
            elif course['level'] == current_level + 1:
                score += 2
                reasons.append("Next level progression")
            elif course['level'] == current_level - 1:
                score += 1
            elif course['level'] > current_level + 1:
                score -= 2  # Too advanced
            
            # 3. Interest matching
            for interest in profile.interests:
                if interest.lower() in course['name'].lower():
                    score += 3
                    reasons.append(f"Matches your interest in {interest}")
                    break
            
            # 4. Career goal alignment
            career_lower = profile.careerGoals.lower()
            course_name_lower = course['name'].lower()
            
            career_keywords = {
                'machine learning': ['machine learning', 'ml', 'ai', 'neural'],
                'data': ['data', 'analytics', 'statistics'],
                'web': ['web', 'frontend', 'backend', 'full-stack'],
                'security': ['security', 'cyber', 'cryptography'],
                'software': ['software', 'engineering', 'development']
            }
            
            for goal_key, keywords in career_keywords.items():
                if goal_key in career_lower:
                    if any(kw in course_name_lower for kw in keywords):
                        score += 2
                        reasons.append("Aligns with career goals")
                        break
            
            # 5. Prerequisite check
            prereqs = course.get('prerequisites', '')
            completed = set(profile.completedCourses)
            
            if prereqs and prereqs != 'None':
                prereq_codes = re.findall(r'[A-Z]{2,4}\d{3}', prereqs)
                if prereq_codes:
                    if any(p in completed for p in prereq_codes):
                        score += 2
                        reasons.append("Prerequisites satisfied")
                    else:
                        score -= 5  # Cannot take yet
            else:
                score += 1  # No prerequisites needed
            
            # Only include courses with positive scores
            if score > 0:
                scored.append({
                    'course': course,
                    'score': score,
                    'reasons': reasons
                })
        
        # Sort by score (highest first)
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        return scored