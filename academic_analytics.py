
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt



class AcademicAnalytics:
    """Simple academic performance analytics for Uni Assist."""

    def __init__(self, data_dir=None):
        self.data_dir = (
            Path(data_dir)
            if data_dir is not None
            else Path(__file__).resolve().parent / "uni_assist_dataset"
        )

        self.students = pd.read_csv(self.data_dir / "students.csv")
        self.courses = pd.read_csv(self.data_dir / "courses.csv")
        self.grades = pd.read_csv(self.data_dir / "grades.csv")
        self.activity = pd.read_csv(
            self.data_dir / "student_activity.csv"
        )
        
    def create_semester_chart(self, student_id):
        result = self.analyze_student(student_id)
        trends = result["semester_trends"]

        if not trends:
            print("No semester data available to create a chart.")
            return

        semesters = [item["semester"] for item in trends]
        averages = [item["average_grade"] for item in trends]

        plt.figure(figsize=(8, 5))
        plt.plot(semesters, averages, marker="o")
        plt.title(f"Semester Performance - {student_id}")
        plt.xlabel("Semester")
        plt.ylabel("Average Grade")
        plt.ylim(0, 100)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.show()
        plt.close()
    
    def analyze_student(self, student_id):
        # Find the student.
        student_rows = self.students[
            self.students["student_id"].astype(str) == str(student_id)
        ]

        if student_rows.empty:
            raise ValueError(f"Student ID '{student_id}' was not found.")

        student = student_rows.iloc[0]

        # Get this student's grade records.
        grades = self.grades[
            self.grades["student_id"].astype(str) == str(student_id)
        ].copy()

        if grades.empty:
            raise ValueError(
                f"No grade records found for student '{student_id}'."
            )

        grades["numeric_grade"] = pd.to_numeric(
            grades["numeric_grade"], errors="coerce"
        )
        grades = grades.dropna(subset=["numeric_grade"])

        if grades.empty:
            raise ValueError("This student has no valid numeric grades.")
        
        # Analyze performance across semesters.
        semester_trends = []

        if "semester" in grades.columns:
            semester_averages = (
                grades.groupby("semester")["numeric_grade"]
                .mean()
                .reset_index()
            )

            semester_order = {
                "Fall 2024": 1,
                "Spring 2025": 2,
                "Fall 2025": 3,
                "Spring 2026": 4,
            }

            semester_averages["order"] = (
                semester_averages["semester"]
                .map(semester_order)
                .fillna(999)
            )

            semester_averages = semester_averages.sort_values("order")

            for _, row in semester_averages.iterrows():
                semester_trends.append({
                    "semester": str(row["semester"]),
                    "average_grade": round(
                        float(row["numeric_grade"]), 2
                    ),
                })

        trend_change = None

        if len(semester_trends) >= 2:
            trend_change = round(
                semester_trends[-1]["average_grade"]
                - semester_trends[-2]["average_grade"],
                2,
            )
            
        
        # Calculate academic performance.
        average_grade = float(grades["numeric_grade"].mean())
        passed = int((grades["numeric_grade"] >= 60).sum())
        failed = int((grades["numeric_grade"] < 60).sum())

        # Find strongest and weakest subjects using average grades.
        course_results = (
            grades.groupby("course_id")["numeric_grade"]
            .mean()
            .reset_index()
            .merge(self.courses[["course_id", "course_name"]], on="course_id")
            .sort_values("numeric_grade", ascending=False)
        )

        strongest = course_results.iloc[0]
        weakest = course_results.iloc[-1]

        # Get activity data for this student.
        activity = self.activity[
            self.activity["student_id"].astype(str) == str(student_id)
        ].copy()

        activity_summary = {}

        for column in [
            "attendance_pct",
            "study_hours_per_week",
            "quiz_avg",
            "assignment_completion_pct",
        ]:
            if column in activity.columns and not activity.empty:
                values = pd.to_numeric(activity[column], errors="coerce").dropna()
                activity_summary[column] = (
                    round(float(values.mean()), 2)
                    if not values.empty
                    else None
                )
            else:
                activity_summary[column] = None

        # Transparent support indicators, not a predictive diagnosis.
        support_reasons = []

        if average_grade < 60:
            support_reasons.append("Average grade is below 60.")
        if failed > 0:
            support_reasons.append(f"{failed} historical course result(s) below 60.")

        attendance = activity_summary["attendance_pct"]
        if attendance is not None and attendance < 75:
            support_reasons.append("Average attendance is below 75%.")

        assignment_completion = activity_summary["assignment_completion_pct"]
        if assignment_completion is not None and assignment_completion < 70:
            support_reasons.append("Assignment completion is below 70%.")

        return {
            "student": {
                "student_id": str(student["student_id"]),
                "student_name": str(student["student_name"]),
                "department_name": str(student["department_name"]),
                "year_level": int(student["year_level"]),
                "gpa": float(student["gpa"]),
            },
            "performance": {
                "average_grade": round(average_grade, 2),
                "courses_with_grades": int(grades["course_id"].nunique()),
                "passed_records": passed,
                "failed_records": failed,
                "pass_rate_pct": round(passed / len(grades) * 100, 2),
            },
            "strongest_course": {
                "course_name": str(strongest["course_name"]),
                "average_grade": round(float(strongest["numeric_grade"]), 2),
            },
            "weakest_course": {
                "course_name": str(weakest["course_name"]),
                "average_grade": round(float(weakest["numeric_grade"]), 2),
            },
            "semester_trends": semester_trends,
            "trend_change": trend_change,
            "activity": activity_summary,
            "support_reasons": support_reasons,
            "note": (
                "Results use synthetic historical records. Support indicators "
                "are transparent prototype rules, not a clinical or validated "
                "prediction of student outcomes."
            ),
        }

    def print_report(self, student_id):
        result = self.analyze_student(student_id)
        student = result["student"]
        performance = result["performance"]

        print(f"\nAcademic Analytics: {student['student_name']}")
        print(
            f"Department: {student['department_name']} | "
            f"Year: {student['year_level']} | GPA: {student['gpa']:.2f}/4.00"
        )

        print("\n--- Academic Performance ---")
        print(f"Average grade: {performance['average_grade']:.2f}/100")
        print(f"Courses with grades: {performance['courses_with_grades']}")
        print(f"Passing records: {performance['passed_records']}")
        print(f"Below-passing records: {performance['failed_records']}")
        print(f"Pass rate: {performance['pass_rate_pct']:.2f}%")

        print("\n--- Subject Strengths and Weaknesses ---")
        print(
            f"Strongest: {result['strongest_course']['course_name']} "
            f"({result['strongest_course']['average_grade']:.2f})"
        )
        print(
            f"Needs review: {result['weakest_course']['course_name']} "
            f"({result['weakest_course']['average_grade']:.2f})"
        )
        print("\n--- Semester-by-Semester Trends ---")

        trends = result["semester_trends"]

        if trends:
            for item in trends:
                print(
                    f"{item['semester']}: "
                    f"{item['average_grade']:.2f}/100"
                )
        else:
            print("No semester trend data available.")

        change = result["trend_change"]

        if change is not None:
            if change > 0:
                print(f"Performance improved by {change:.2f} points.")
            elif change < 0:
                print(f"Performance declined by {abs(change):.2f} points.")
            else:
                print("Performance stayed the same.")
        else:
            print("Not enough semester data to calculate a trend.")

        print("\n--- Study Activity Averages ---")
        labels = {
            "attendance_pct": "Attendance",
            "study_hours_per_week": "Study hours per week",
            "quiz_avg": "Quiz average",
            "assignment_completion_pct": "Assignment completion",
        }

        for key, label in labels.items():
            value = result["activity"][key]
            print(f"{label}: {value if value is not None else 'No data'}")

        print("\n--- Academic Support Indicators ---")
        if result["support_reasons"]:
            for reason in result["support_reasons"]:
                print(f"- {reason}")
        else:
            print("No support indicators triggered by the current rules.")

        print(f"\nNote: {result['note']}")
        self.create_semester_chart(student_id)


if __name__ == "__main__":
    student_id = input("Student ID (for example S0001): ").strip()

    try:
        analytics = AcademicAnalytics()
        analytics.print_report(student_id)
    except (ValueError, FileNotFoundError) as error:
        print(f"Could not analyze student: {error}")
