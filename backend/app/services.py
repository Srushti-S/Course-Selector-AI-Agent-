"""
Course Recommendation Service — Enhanced with LangChain + Fallback
"""
from typing import List, Optional, Tuple
import re
import os
import math
import logging
from datetime import date

from pydantic import BaseModel

from app.models import StudentProfile, Recommendation, SemesterPlan
from app.data import COURSE_CATALOG

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


def cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def course_summary(course: dict) -> str:
    return (
        f"{course['code']} {course['name']} ({course['credits']} cr, level {course['level']}, "
        f"{course['major']}, prereqs: {course['prerequisites']})"
    )


class AiRecommendation(BaseModel):
    courseCode: str
    reason: str = ""
    priority: str = "medium"
    semester: str = ""


class AiRecommendations(BaseModel):
    items: List[AiRecommendation]


class AiPlanCourse(BaseModel):
    courseCode: str
    reason: str = ""


class AiPlanSemester(BaseModel):
    semester: str
    courses: List[AiPlanCourse] = []


class AiPlan(BaseModel):
    semesters: List[AiPlanSemester]


class CourseRecommendationService:
    """Service for generating course recommendations using AI or rule-based fallback."""

    def __init__(self):
        self.ai_enabled = False
        self._llm = None
        self._rec_chain = None
        self._plan_chain = None
        self._embeddings = None
        self._catalog_vectors = None
        self._embed_failures = 0
        self._last_query = None
        self._last_query_vector = None
        self._init_ai()

    def _init_ai(self):
        """Try to initialize LangChain with OpenAI. Falls back gracefully."""
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or api_key.startswith("your-"):
            logger.info("No OpenAI API key — using rule-based recommendations.")
            return
        try:
            from langchain_openai import ChatOpenAI, OpenAIEmbeddings
            from langchain_core.prompts import ChatPromptTemplate

            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self._llm = ChatOpenAI(model=model, temperature=0, timeout=45)
            self._embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

            rec_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an academic advisor. Recommend 6-8 courses from the catalog "
                        "for this student. Use only course codes that appear in the catalog. "
                        "Prefer courses whose prerequisites the student has completed, and give "
                        "each pick a specific one-sentence reason tied to the student's goals. "
                        "Priority is high, medium, or low. Semester must be one of the given labels.",
                    ),
                    (
                        "human",
                        "Student profile:\n{profile}\n\nSemester labels: {semesters}\n\n"
                        "Course catalog:\n{courses}",
                    ),
                ]
            )
            plan_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an academic advisor building a multi-semester schedule. "
                        "Assign catalog courses to the given semester labels. Never include "
                        "courses the student already completed. A course's prerequisites must "
                        "all be completed or scheduled in an earlier semester. Keep each "
                        "semester at or under the credit limit and reasonably full. Favor the "
                        "student's major, interests, and career goals.",
                    ),
                    (
                        "human",
                        "Student profile:\n{profile}\n\nSemester labels: {semesters}\n\n"
                        "Credit limit per semester: {max_credits}\n\nCourse catalog:\n{courses}",
                    ),
                ]
            )
            self._rec_chain = rec_prompt | self._llm.with_structured_output(AiRecommendations)
            self._plan_chain = plan_prompt | self._llm.with_structured_output(AiPlan)
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

    def _semantic_scores(self, profile: StudentProfile) -> Optional[dict]:
        if not self._embeddings:
            return None
        query = " ".join(profile.interests + [profile.careerGoals]).strip()
        if not query:
            return None
        try:
            if self._catalog_vectors is None:
                texts = [f"{c['name']}. {c.get('description', '')}" for c in COURSE_CATALOG]
                vectors = self._embeddings.embed_documents(texts)
                self._catalog_vectors = {
                    c["code"]: v for c, v in zip(COURSE_CATALOG, vectors)
                }
            if query != self._last_query:
                self._last_query_vector = self._embeddings.embed_query(query)
                self._last_query = query
            self._embed_failures = 0
            return {
                code: cosine(self._last_query_vector, vector)
                for code, vector in self._catalog_vectors.items()
            }
        except Exception as e:
            logger.warning(f"Embeddings unavailable, using keyword matching: {e}")
            self._embed_failures += 1
            if self._embed_failures >= 3:
                self._embeddings = None
            return None

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
        result = self._rec_chain.invoke(
            {
                "profile": self._profile_str(profile),
                "semesters": ", ".join(semesters),
                "courses": "\n".join(course_summary(c) for c in available),
            }
        )

        recommendations = []
        seen = set()
        for item in result.items:
            code = item.courseCode.strip().upper()
            course = by_code.get(code)
            if course is None or code in seen:
                continue
            seen.add(code)
            priority = item.priority.strip().lower()
            if priority not in PRIORITIES:
                priority = "medium"
            semester = item.semester if item.semester in semesters else semesters[0]
            reason = item.reason.strip() or "Recommended for your program"
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
        similarities = self._semantic_scores(profile)

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
            if similarities is not None:
                sim = similarities.get(course["code"], 0.0)
                if sim >= 0.4:
                    score += 4
                    reasons.append("Strong match for your interests and goals")
                elif sim >= 0.3:
                    score += 2
                    reasons.append("Related to your interests")
            else:
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

        result = self._plan_chain.invoke(
            {
                "profile": self._profile_str(profile),
                "semesters": ", ".join(semesters),
                "max_credits": max_credits,
                "courses": "\n".join(course_summary(c) for c in available),
            }
        )
        proposed = {
            entry.semester: entry.courses
            for entry in result.semesters
            if entry.semester in semesters
        }

        plan = []
        satisfied = set(completed)
        used = set()
        for sem_index, sem_label in enumerate(semesters):
            completed_before = set(satisfied)
            sem_courses = []
            sem_credits = 0
            rec_id = sem_index * 10 + 1
            for item in proposed.get(sem_label, []):
                code = item.courseCode.strip().upper()
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
                        item.reason.strip() or "Scheduled by your AI advisor",
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
