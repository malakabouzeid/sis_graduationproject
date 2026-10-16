# Uni Assist Synthetic Dataset

All records are synthetic and created for a university project prototype. They do not represent real students or institutional records.

## Included files
- `students.csv`: 150 synthetic student profiles with department, year level, and GPA (0-4 scale).
- `courses.csv`: 18 courses across Computer Science, Information Technology, and Business Administration, with credits, year level, and prerequisite IDs.
- `enrollments.csv`: historical completed enrollments plus Fall 2026 current enrollments.
- `grades.csv`: historical course grades and assessment component scores, including numeric grade, letter grade, quiz, assignment, midterm, and final exam scores.
- `student_activity.csv`: course-level attendance, study hours, quiz average, assignment completion, late submissions, and preferred study period.
- `semester_summary.csv`: student/semester aggregate metrics for analytics.

## Compatibility
The first four CSV files are designed for the current Uni Assist `CourseRecommender`:
- students: `student_id`, `student_name`, `department_id`, `department_name`, `year_level`, `gpa`
- courses: `course_id`, `course_name`, `department_id`, `department_name`, `year_level`, `credits`, `prerequisite_course_id`
- enrollments: `enrollment_id`, `student_id`, `course_id`, `semester`, `enrollment_status`
- grades: `grade_id`, `student_id`, `course_id`, `semester`, `numeric_grade`, `letter_grade`, `credits`, `quiz_score`, `assignment_score`, `midterm_exam_score`, `final_exam_score`

## Academic Analytics
Use grades, students, courses, enrollments, student activity, and semester summary to build performance summaries, trends, strengths/weaknesses, and transparent academic-support flags.

## Limitations
Synthetic demonstration data is not validated institutional data. Use it to test code and demonstrate features, not for real academic decisions.
