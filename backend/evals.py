"""
Offline evals for the recommendation and planning engine.
Run from backend/: python evals.py
"""
import itertools
import statistics
import time

from dotenv import load_dotenv

from app.data import COURSE_CATALOG
from app.models import StudentProfile
from app.services import CourseRecommendationService, parse_prereqs

MAJORS = [
    "Computer Science", "Data Science", "Software Engineering",
    "Information Systems", "Cybersecurity", "Artificial Intelligence",
]
YEARS = ["Freshman", "Sophomore", "Junior", "Senior"]
COMPLETED_BY_YEAR = {
    "Freshman": [],
    "Sophomore": ["CS101", "MATH201"],
    "Junior": ["CS101", "CS102", "CS201", "MATH201", "STAT101"],
    "Senior": ["CS101", "CS102", "CS201", "CS202", "CS250", "CS301", "MATH201", "MATH202", "STAT101"],
}
INTEREST_SETS = [
    (["Machine Learning"], "Become a machine learning engineer"),
    (["Web Development", "Cloud Computing"], "Full-stack developer at a startup"),
    (["Cybersecurity"], "Security analyst at a large company"),
]


def build_profiles():
    profiles = []
    for major, year in itertools.product(MAJORS, YEARS):
        interests, goal = INTEREST_SETS[len(profiles) % len(INTEREST_SETS)]
        profiles.append(
            StudentProfile(
                name=f"Student {len(profiles) + 1}",
                major=major,
                year=year,
                completedCourses=COMPLETED_BY_YEAR[year],
                interests=interests,
                careerGoals=goal,
                creditHoursPerSemester=15,
            )
        )
    return profiles


def count_prereq_violations(plan, completed):
    done = set(completed)
    violations = 0
    for semester in plan:
        for course in semester.courses:
            for code in parse_prereqs(course.prerequisites):
                if code not in done:
                    violations += 1
        done.update(c.courseCode for c in semester.courses)
    return violations


def count_interest_matches(recommendations, profile):
    terms = [t.lower() for t in profile.interests]
    matches = 0
    for rec in recommendations:
        text = f"{rec.courseName} {rec.description or ''}".lower()
        if any(term in text for term in terms):
            matches += 1
    return matches


def main():
    load_dotenv()
    service = CourseRecommendationService()
    profiles = build_profiles()

    violations = 0
    utilizations = []
    plan_sizes = []
    latencies = []
    rec_matches = 0
    rec_total = 0
    sources = set()

    for profile in profiles:
        start = time.perf_counter()
        source, plan = service.generate_semester_plan(profile, COURSE_CATALOG)
        latencies.append(time.perf_counter() - start)
        sources.add(source)

        violations += count_prereq_violations(plan, profile.completedCourses)
        plan_sizes.append(sum(len(s.courses) for s in plan))
        if plan:
            cap = profile.creditHoursPerSemester * len(plan)
            utilizations.append(sum(s.totalCredits for s in plan) / cap)

        _, recommendations = service.generate_recommendations(profile, COURSE_CATALOG)
        rec_matches += count_interest_matches(recommendations, profile)
        rec_total += len(recommendations)

    print(f"profiles evaluated:      {len(profiles)}")
    print(f"planner source(s):       {', '.join(sorted(sources))}")
    print(f"prereq violations:       {violations}")
    print(f"avg credit utilization:  {statistics.mean(utilizations):.0%}")
    print(f"avg courses per plan:    {statistics.mean(plan_sizes):.1f}")
    print(f"interest match rate:     {rec_matches / max(rec_total, 1):.0%}")
    print(f"avg plan latency:        {statistics.mean(latencies) * 1000:.1f} ms")


if __name__ == "__main__":
    main()
