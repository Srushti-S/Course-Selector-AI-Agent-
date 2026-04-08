"""
Course Recommendation Service — Enhanced with LangChain + Fallback
"""
from typing import List
import re
import os
import json
import logging

from app.models import StudentProfile, Recommendation, SemesterPlan

logger = logging.getLogger(__name__)


class CourseRecommendationService:
    """Service for generating course recommendations using AI or rule-based fallback."""

    def __init__(self):
        self.ai_enabled = False
        self._chain = None
        self._init_ai()

    def _init_ai(self):
        """Try to initialize LangChain with OpenAI. Falls back gracefully."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            logger.info("No OpenAI API key — using rule-based recommendations.")
            return
        try:
            from langchain_openai import ChatOpenAI
            from langchain.prompts import ChatPromptTemplate
            from langchain.output_parsers import PydanticOutputParser

            self._llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
            self._prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an expert academic advisor. Given a student profile and "
                        "available courses, recommend the best courses. Return a JSON array of objects "
                        "with fields: courseCode, courseName, credits, semester, reason, priority "
                        "(high/medium/low), prerequisites, description, level, major. "
                        "Recommend 6-8 courses. Be specific in your reasoning.",
                    ),
                    (
                        "human",
                        "Student profile:\n{profile}\n\nAvailable courses:\n{courses}\n\n"
                        "Return ONLY valid JSON — an array of recommendation objects.",
                    ),
                ]
            )
            self._chain = self._prompt | self._llm
            self.ai_enabled = True
            logger.info("LangChain AI recommendations enabled.")
        except Exception as e:
            logger.warning(f"Failed to initialize AI: {e}")

    def generate_recommendations(
        self, profile: StudentProfile, course_catalog: List[dict]
    ) -> List[Recommendation]:
        completed = set(profile.completedCourses)
        available = [c for c in course_catalog if c["code"] not in completed]

        if self.ai_enabled and self._chain:
            try:
                return self._ai_recommendations(profile, available)
            except Exception as e:
                logger.warning(f"AI recommendation failed, falling back: {e}")

        return self._rule_based_recommendations(profile, available)

    def _ai_recommendations(
        self, profile: StudentProfile, available: List[dict]
    ) -> List[Recommendation]:
        """Generate recommendations using LangChain."""
        profile_str = (
            f"Name: {profile.name}, Major: {profile.major}, Year: {profile.year}, "
            f"Completed: {', '.join(profile.completedCourses) or 'None'}, "
            f"Interests: {', '.join(profile.interests) or 'None'}, "
            f"Career Goals: {profile.careerGoals}, "
            f"Credit Hours/Semester: {profile.creditHoursPerSemester}"
        )
        courses_str = json.dumps(available[:25], indent=1) 
        response = self._chain.invoke(
            {"profile": profile_str, "courses": courses_str}
        )
        raw = response.content.strip()
    
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)

        recommendations = []
        for i, item in enumerate(data[:8], start=1):
            recommendations.append(
                Recommendation(
                    id=i,
                    courseCode=item.get("courseCode", ""),
                    courseName=item.get("courseName", ""),
                    credits=item.get("credits", 3),
                    semester=item.get("semester", "Fall 2025"),
                    reason=item.get("reason", ""),
                    priority=item.get("priority", "medium"),
                    prerequisites=item.get("prerequisites", "None"),
                    description=item.get("description", ""),
                    level=item.get("level"),
                    major=item.get("major"),
                )
            )
        return recommendations

    def _rule_based_recommendations(
        self, profile: StudentProfile, available: List[dict]
    ) -> List[Recommendation]:
        """Enhanced rule-based scoring with richer reasoning."""
        scored = self._score_courses(profile, available)

        recommendations = []
        semesters = ["Fall 2025", "Spring 2026", "Fall 2026", "Spring 2027"]
        for i, item in enumerate(scored[:8], start=1):
            course = item["course"]
            score = item["score"]
            reasons = item["reasons"]

            priority = "high" if score >= 8 else ("medium" if score >= 5 else "low")
            reason = "; ".join(reasons) if reasons else "Recommended for your program"
            semester = semesters[min(i - 1, len(semesters) - 1) // 2]

            recommendations.append(
                Recommendation(
                    id=i,
                    courseCode=course["code"],
                    courseName=course["name"],
                    credits=course["credits"],
                    semester=semester,
                    reason=reason,
                    priority=priority,
                    prerequisites=course.get("prerequisites", "None"),
                    description=course.get("description", ""),
                    level=course.get("level"),
                    major=course.get("major"),
                )
            )
        return recommendations

    def _score_courses(
        self, profile: StudentProfile, available: List[dict]
    ) -> List[dict]:
        year_to_level = {"Freshman": 1, "Sophomore": 2, "Junior": 3, "Senior": 4}
        current_level = year_to_level.get(profile.year, 2)
        completed = set(profile.completedCourses)

        major_prefixes = {
            "Computer Science": ["CS"],
            "Data Science": ["DS", "CS"],
            "Software Engineering": ["SE", "CS"],
            "Information Systems": ["IS", "CS"],
            "Cybersecurity": ["CY", "CS"],
            "Artificial Intelligence": ["CS", "DS"],
        }
        relevant_prefixes = major_prefixes.get(profile.major, ["CS"])

        career_keywords = {
            "machine learning": ["machine learning", "ml", "ai", "neural", "deep learning"],
            "data": ["data", "analytics", "statistics", "mining"],
            "web": ["web", "frontend", "backend", "full-stack", "full stack"],
            "security": ["security", "cyber", "cryptography", "hacking", "network security"],
            "software": ["software", "engineering", "development", "devops", "architecture"],
            "mobile": ["mobile", "ios", "android", "app development"],
            "cloud": ["cloud", "distributed", "aws", "azure"],
            "ai": ["artificial intelligence", "ai", "nlp", "computer vision", "neural"],
        }

        scored = []
        for course in available:
            score = 0
            reasons = []
            code_prefix = re.match(r"[A-Z]+", course["code"])
            code_prefix = code_prefix.group() if code_prefix else ""

            if code_prefix in relevant_prefixes:
                score += 5
                reasons.append(f"Core {profile.major} requirement")

            if course["level"] == current_level:
                score += 3
                reasons.append(f"Ideal for your {profile.year} year")
            elif course["level"] == current_level + 1:
                score += 2
                reasons.append("Prepares you for next year")
            elif course["level"] == current_level - 1:
                score += 1
            elif course["level"] > current_level + 1:
                score -= 2

            course_text = f"{course['name']} {course.get('description', '')}".lower()
            for interest in profile.interests:
                if interest.lower() in course_text:
                    score += 4
                    reasons.append(f"Matches your interest in {interest}")
                    break

            career_lower = profile.careerGoals.lower()
            for goal_key, keywords in career_keywords.items():
                if goal_key in career_lower:
                    if any(kw in course_text for kw in keywords):
                        score += 3
                        reasons.append("Aligns with your career goals")
                        break
            prereqs_str = course.get("prerequisites", "None")
            if prereqs_str and prereqs_str != "None":
                prereq_codes = re.findall(r"[A-Z]{2,4}\d{3}", prereqs_str)
                if prereq_codes:
                    met = [p for p in prereq_codes if p in completed]
                    if len(met) == len(prereq_codes):
                        score += 3
                        reasons.append("All prerequisites completed")
                    elif len(met) > 0:
                        score += 1
                        reasons.append(f"Partial prerequisites met ({len(met)}/{len(prereq_codes)})")
                    else:
                        score -= 6
            else:
                score += 1

            if score > 0:
                scored.append({"course": course, "score": score, "reasons": reasons})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def generate_semester_plan(
        self, profile: StudentProfile, course_catalog: List[dict]
    ) -> List[SemesterPlan]:
        """Generate a multi-semester plan respecting credit limits and prerequisites."""
        completed = set(profile.completedCourses)
        available = [c for c in course_catalog if c["code"] not in completed]
        max_credits = profile.creditHoursPerSemester

        semesters_labels = ["Fall 2025", "Spring 2026", "Fall 2026", "Spring 2027"]
        plan = []
        planned_codes = set(completed)

        for sem_label in semesters_labels:
            profile_copy = profile.model_copy()
            profile_copy.completedCourses = list(planned_codes)
            remaining = [c for c in course_catalog if c["code"] not in planned_codes]
            scored = self._score_courses(profile_copy, remaining)

            sem_courses = []
            sem_credits = 0
            rec_id = len(plan) * 10 + 1

            for item in scored:
                course = item["course"]
                if sem_credits + course["credits"] > max_credits:
                    continue
                prereqs_str = course.get("prerequisites", "None")
                if prereqs_str and prereqs_str != "None":
                    prereq_codes = re.findall(r"[A-Z]{2,4}\d{3}", prereqs_str)
                    if not all(p in planned_codes for p in prereq_codes):
                        continue

                sem_courses.append(
                    Recommendation(
                        id=rec_id,
                        courseCode=course["code"],
                        courseName=course["name"],
                        credits=course["credits"],
                        semester=sem_label,
                        reason="; ".join(item["reasons"]),
                        priority="high" if item["score"] >= 8 else "medium" if item["score"] >= 5 else "low",
                        prerequisites=course.get("prerequisites", "None"),
                        description=course.get("description", ""),
                        level=course.get("level"),
                        major=course.get("major"),
                    )
                )
                sem_credits += course["credits"]
                planned_codes.add(course["code"])
                rec_id += 1
                if sem_credits >= max_credits - 2:
                    break

            if sem_courses:
                plan.append(
                    SemesterPlan(
                        semester=sem_label,
                        courses=sem_courses,
                        totalCredits=sem_credits,
                    )
                )

        return plan
