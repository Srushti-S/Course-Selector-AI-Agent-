"""
Course Recommendation Service — Enhanced with LangChain + Fallback
"""
from typing import List, Tuple
import re
import os
import json
import logging
from datetime import date

from app.models import StudentProfile, Recommendation, SemesterPlan

logger = logging.getLogger(__name__)

PREREQ_PATTERN = re.compile(r"[A-Z]{2,4}\d{3}")
PRIORITIES = {"high", "medium", "low"}


def parse_prereqs(prereq_str) -> List[str]:
    if not prereq_str or prereq_str == "None":
        return []
    return PREREQ_PATTERN.findall(prereq_str)


def upcoming_semesters(count: int = 4) -> List[str]:
    today = date.today()
    if today.month <= 7:
        term, year = "Fall", today.year
    else:
        term, year = "Spring", today.year + 1
    labels = []
    for _ in range(count):
        labels.append(f"{term} {year}")
        if term == "Fall":
            term, year = "Spring", year + 1
        else:
            term = "Fall"
    return labels


def compact_courses(courses: List[dict]) -> str:
    fields = ("code", "name", "credits", "level", "major", "prerequisites")
    return json.dumps(
        [{k: c[k] for k in fields} for c in courses], separators=(",", ":")
    )


class CourseRecommendationService:
    """Service for generating course recommendations using AI or rule-based fallback."""

    def __init__(self):
        self.ai_enabled = False
        self._llm = None
        self._rec_chain = None
        self._plan_chain = None
        self._init_ai()

    def _init_ai(self):
        """Try to initialize LangChain with OpenAI. Falls back gracefully."""
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or api_key.startswith("your-"):
            logger.info("No OpenAI API key — using rule-based recommendations.")
            return
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate

            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self._llm = ChatOpenAI(model=model, temperature=0, timeout=45)

            rec_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an expert academic advisor. Given a student profile and the "
                        "available course catalog, recommend the best courses for this student. "
                        "Return ONLY a JSON array of 6-8 objects, each with fields: "
                        "courseCode (must be a code from the catalog), reason (one specific "
                        "sentence tailored to this student), priority (high/medium/low), and "
                        "semester (one of the provided semester labels). Prefer courses whose "
                        "prerequisites the student has completed.",
                    ),
                    (
                        "human",
                        "Student profile:\n{profile}\n\nSemester labels: {semesters}\n\n"
                        "Course catalog:\n{courses}\n\nReturn ONLY the JSON array.",
                    ),
                ]
            )
            plan_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an expert academic advisor building a multi-semester schedule. "
                        "Given a student profile, a course catalog, semester labels, and a "
                        "per-semester credit limit, assign courses to semesters. Rules: never "
                        "include courses the student already completed; a course's prerequisites "
                        "must all be either already completed or scheduled in an EARLIER semester; "
                        "each semester's total credits must not exceed the limit and should be "
                        "close to it; favor courses matching the student's major, interests, and "
                        "career goals. Return ONLY a JSON array with one object per semester "
                        "label, each with fields: semester (the label) and courses (array of "
                        "objects with courseCode and reason).",
                    ),
                    (
                        "human",
                        "Student profile:\n{profile}\n\nSemester labels: {semesters}\n\n"
                        "Credit limit per semester: {max_credits}\n\nCourse catalog:\n{courses}\n\n"
                        "Return ONLY the JSON array.",
                    ),
                ]
            )
            self._rec_chain = rec_prompt | self._llm
            self._plan_chain = plan_prompt | self._llm
            self.ai_enabled = True
            logger.info("LangChain AI recommendations enabled (model=%s).", model)
        except Exception as e:
            logger.warning(f"Failed to initialize AI: {e}")

    @staticmethod
    def _profile_str(profile: StudentProfile) -> str:
        return (
            f"Name: {profile.name}, Major: {profile.major}, Year: {profile.year}, "
            f"Completed: {', '.join(profile.completedCourses) or 'None'}, "
            f"Interests: {', '.join(profile.interests) or 'None'}, "
            f"Career Goals: {profile.careerGoals}, "
            f"Credit Hours/Semester: {profile.creditHoursPerSemester}"
        )

    @staticmethod
    def _extract_json_array(raw: str):
        text = raw.strip()
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end <= start:
            raise ValueError("No JSON array found in model response")
        data = json.loads(text[start : end + 1])
        if not isinstance(data, list):
            raise ValueError("Model response is not a JSON array")
        return data

    def _course_to_recommendation(
        self, course: dict, rec_id: int, semester: str, reason: str, priority: str
    ) -> Recommendation:
        return Recommendation(
            id=rec_id,
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

    def generate_recommendations(
        self, profile: StudentProfile, course_catalog: List[dict]
    ) -> Tuple[str, List[Recommendation]]:
        completed = set(profile.completedCourses)
        available = [c for c in course_catalog if c["code"] not in completed]

        if self.ai_enabled and self._rec_chain:
            try:
                recommendations = self._ai_recommendations(profile, available)
                if recommendations:
                    return "ai", recommendations
                logger.warning("AI returned no usable recommendations, falling back.")
            except Exception as e:
                logger.warning(f"AI recommendation failed, falling back: {e}")

        return "rules", self._rule_based_recommendations(profile, available)

    def _ai_recommendations(
        self, profile: StudentProfile, available: List[dict]
    ) -> List[Recommendation]:
        """Generate recommendations using LangChain."""
        by_code = {c["code"]: c for c in available}
        semesters = upcoming_semesters()
        response = self._rec_chain.invoke(
            {
                "profile": self._profile_str(profile),
                "semesters": ", ".join(semesters),
                "courses": compact_courses(available),
            }
        )
        data = self._extract_json_array(response.content)

        recommendations = []
        seen = set()
        for item in data:
            if not isinstance(item, dict):
                continue
            code = str(item.get("courseCode", "")).strip().upper()
            course = by_code.get(code)
            if course is None or code in seen:
                continue
            seen.add(code)
            priority = str(item.get("priority", "medium")).strip().lower()
            if priority not in PRIORITIES:
                priority = "medium"
            semester = item.get("semester")
            if semester not in semesters:
                semester = semesters[0]
            reason = str(item.get("reason") or "Recommended for your program").strip()
            recommendations.append(
                self._course_to_recommendation(
                    course, len(recommendations) + 1, semester, reason, priority
                )
            )
            if len(recommendations) == 8:
                break
        return recommendations

    def _rule_based_recommendations(
        self, profile: StudentProfile, available: List[dict]
    ) -> List[Recommendation]:
        """Enhanced rule-based scoring with richer reasoning."""
        scored = self._score_courses(profile, available)
        semesters = upcoming_semesters()

        recommendations = []
        for i, item in enumerate(scored[:8], start=1):
            course = item["course"]
            score = item["score"]
            reasons = item["reasons"]

            priority = "high" if score >= 8 else ("medium" if score >= 5 else "low")
            reason = "; ".join(reasons) if reasons else "Recommended for your program"
            semester = semesters[min((i - 1) // 2, len(semesters) - 1)]

            recommendations.append(
                self._course_to_recommendation(course, i, semester, reason, priority)
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

        career_lower = profile.careerGoals.lower()
        matched_keywords = set()
        for goal_key, keywords in career_keywords.items():
            if goal_key in career_lower or any(kw in career_lower for kw in keywords):
                matched_keywords.update(keywords)

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

            if matched_keywords and any(kw in course_text for kw in matched_keywords):
                score += 3
                reasons.append("Aligns with your career goals")

            prereq_codes = parse_prereqs(course.get("prerequisites", "None"))
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
    ) -> Tuple[str, List[SemesterPlan]]:
        """Generate a multi-semester plan respecting credit limits and prerequisites."""
        if self.ai_enabled and self._plan_chain:
            try:
                plan = self._ai_semester_plan(profile, course_catalog)
                if plan:
                    return "ai", plan
                logger.warning("AI returned no usable plan, falling back.")
            except Exception as e:
                logger.warning(f"AI plan failed, falling back: {e}")

        return "rules", self._rule_based_semester_plan(profile, course_catalog)

    def _ai_semester_plan(
        self, profile: StudentProfile, course_catalog: List[dict]
    ) -> List[SemesterPlan]:
        completed = set(profile.completedCourses)
        available = [c for c in course_catalog if c["code"] not in completed]
        by_code = {c["code"]: c for c in available}
        semesters = upcoming_semesters()
        max_credits = profile.creditHoursPerSemester

        response = self._plan_chain.invoke(
            {
                "profile": self._profile_str(profile),
                "semesters": ", ".join(semesters),
                "max_credits": max_credits,
                "courses": compact_courses(available),
            }
        )
        data = self._extract_json_array(response.content)

        proposed = {}
        for entry in data:
            if isinstance(entry, dict) and entry.get("semester") in semesters:
                proposed[entry["semester"]] = entry.get("courses") or []

        plan = []
        satisfied = set(completed)
        used = set()
        for sem_index, sem_label in enumerate(semesters):
            completed_before = set(satisfied)
            sem_courses = []
            sem_credits = 0
            rec_id = sem_index * 10 + 1
            for item in proposed.get(sem_label, []):
                if isinstance(item, dict):
                    code = str(item.get("courseCode", "")).strip().upper()
                    reason = str(item.get("reason") or "").strip()
                else:
                    code = str(item).strip().upper()
                    reason = ""
                course = by_code.get(code)
                if course is None or code in used:
                    continue
                if sem_credits + course["credits"] > max_credits:
                    continue
                prereq_codes = parse_prereqs(course.get("prerequisites", "None"))
                if not all(p in completed_before for p in prereq_codes):
                    continue
                sem_courses.append(
                    self._course_to_recommendation(
                        course,
                        rec_id,
                        sem_label,
                        reason or "Scheduled by your AI advisor",
                        "high",
                    )
                )
                sem_credits += course["credits"]
                used.add(code)
                satisfied.add(code)
                rec_id += 1
            if sem_courses:
                plan.append(
                    SemesterPlan(
                        semester=sem_label,
                        courses=sem_courses,
                        totalCredits=sem_credits,
                    )
                )

        if len(used) < min(4, len(available)):
            raise ValueError("AI plan too sparse after validation")
        return plan

    def _rule_based_semester_plan(
        self, profile: StudentProfile, course_catalog: List[dict]
    ) -> List[SemesterPlan]:
        completed = set(profile.completedCourses)
        max_credits = profile.creditHoursPerSemester

        plan = []
        planned_codes = set(completed)

        for sem_index, sem_label in enumerate(upcoming_semesters()):
            completed_before = set(planned_codes)
            profile_copy = profile.model_copy()
            profile_copy.completedCourses = list(completed_before)
            remaining = [c for c in course_catalog if c["code"] not in planned_codes]
            scored = self._score_courses(profile_copy, remaining)

            sem_courses = []
            sem_credits = 0
            rec_id = sem_index * 10 + 1

            for item in scored:
                course = item["course"]
                if sem_credits + course["credits"] > max_credits:
                    continue
                prereq_codes = parse_prereqs(course.get("prerequisites", "None"))
                if not all(p in completed_before for p in prereq_codes):
                    continue

                priority = (
                    "high" if item["score"] >= 8
                    else "medium" if item["score"] >= 5
                    else "low"
                )
                sem_courses.append(
                    self._course_to_recommendation(
                        course,
                        rec_id,
                        sem_label,
                        "; ".join(item["reasons"]) or "Fits your program requirements",
                        priority,
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
