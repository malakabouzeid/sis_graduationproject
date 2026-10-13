from pathlib import Path
import pandas as pd


class CourseRecommender:
    """Simple, explainable course recommender for the Uni Assist prototype."""

    def __init__(self, data_dir=None):
        self.data_dir = (
            Path(data_dir)
            if data_dir is not None
            else Path(__file__).resolve().parent / "uni_assist_dataset"
        )
        self.students = pd.read_csv(self.data_dir / "students.csv")
        self.courses = pd.read_csv(self.data_dir / "courses.csv").fillna("")
        self.enrollments = pd.read_csv(self.data_dir / "enrollments.csv").fillna("")
        self.grades = pd.read_csv(self.data_dir / "grades.csv")
        self.departments = {
            row["department_id"]: row["department_name"]
            for _, row in self.students[["department_id", "department_name"]]
            .drop_duplicates().iterrows()
        }

    def recommend(self, student_id, top_n=5):
        """Return a list of eligible course recommendations with explanations."""
        student_rows = self.students[self.students["student_id"].astype(str) == str(student_id)]
        if student_rows.empty:
            raise ValueError(f"Student ID '{student_id}' was not found.")

        student = student_rows.iloc[0]
        student_id = str(student["student_id"])
        student_dept = str(student["department_id"])
        student_level = int(student["year_level"])

        # Courses already registered in the current semester should not be suggested again.
        current = self.enrollments[
            (self.enrollments["student_id"].astype(str) == student_id)
            & (self.enrollments["semester"] == "Fall 2026")
            & (self.enrollments["enrollment_status"].isin(["Enrolled", "Completed"]))
        ]
        already_registered = set(current["course_id"].astype(str))

        # A prerequisite counts as completed only when a passing grade exists.
        student_grades = self.grades[self.grades["student_id"].astype(str) == student_id]
        passed_courses = set(
            student_grades.loc[student_grades["numeric_grade"] >= 60, "course_id"].astype(str)
        )
        dept_grades = student_grades[
            student_grades["course_id"].isin(
                self.courses.loc[self.courses["department_id"] == student_dept, "course_id"]
            )
        ]
        dept_average = float(dept_grades["numeric_grade"].mean()) if not dept_grades.empty else None

        recommendations = []
        for _, course in self.courses.iterrows():
            course_id = str(course["course_id"])
            prereq = str(course["prerequisite_course_id"]).strip()

            if course_id in already_registered:
                continue

            # Avoid suggesting courses above the student's current year.
            if int(course["year_level"]) > student_level:
                continue

            # Do not recommend a course until its prerequisite has been passed.
            if prereq and prereq not in passed_courses:
                continue

            score = 0
            reasons = []

            if str(course["department_id"]) == student_dept:
                score += 50
                reasons.append("matches your department")
            else:
                score += 15
                reasons.append("offers an option outside your department")

            if int(course["year_level"]) == student_level:
                score += 20
                reasons.append("matches your current year level")
            else:
                score += 10
                reasons.append("is from an earlier year level")

            if prereq:
                score += 15
                reasons.append(f"you passed prerequisite {prereq}")
            else:
                score += 10
                reasons.append("has no listed prerequisite")

            credits = int(course["credits"])
            if credits <= 3:
                score += 10
                reasons.append(f"has a manageable {credits}-credit load")
            else:
                score += 5
                reasons.append(f"requires {credits} credits")

            # Use previous departmental grades only as a small ranking signal.
            if dept_average is not None:
                score += 5 if dept_average >= 75 else 2
                reasons.append("ranked with your previous departmental grades in mind")

            recommendations.append({
                "course_id": course_id,
                "course_name": str(course["course_name"]),
                "department_id": str(course["department_id"]),
                "credits": credits,
                "year_level": int(course["year_level"]),
                "prerequisite": prereq or "None",
                "score": score,
                "reason": "; ".join(reasons) + ".",
            })

        recommendations.sort(key=lambda item: (-item["score"], item["course_id"]))
        return {
            "student": {
                "student_id": student_id,
                "student_name": str(student["student_name"]),
                "department_id": student_dept,
                "department_name": str(student["department_name"]),
                "year_level": student_level,
                "gpa": float(student["gpa"]),
            },
            "recommendations": recommendations[:max(1, int(top_n))],
            "note": (
                "Prototype recommendations based on department, year level, prerequisites, "
                "credits, and previous grades. The dataset is synthetic; validate against "
                "official degree requirements before real academic use."
            ),
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Recommend courses for a student")
    parser.add_argument("student_id", nargs="?", help="student ID, such as S0002")
    parser.add_argument("--top-n", type=int, default=5, help="number of recommendations to show")
    arguments = parser.parse_args()

    student_id = arguments.student_id or input("Enter student ID (for example S0002): ").strip()
    engine = CourseRecommender()
    try:
        result = engine.recommend(student_id, top_n=arguments.top_n)
    except ValueError as error:
        parser.error(str(error))

    print("Student:", result["student"])
    for item in result["recommendations"]:
        print(f'{item["course_id"]}: {item["course_name"]} (score {item["score"]})')
        print("  Why:", item["reason"])
