import argparse
from pathlib import Path

from course_recommender import CourseRecommender
from academic_analytics import AcademicAnalytics
from local_llm import LocalLLMError

ROOT = Path(__file__).resolve().parent


def recommend_courses(student_id, top_n=5):
    recommender = CourseRecommender(data_dir=ROOT / "uni_assist_dataset")
    result = recommender.recommend(student_id, top_n=top_n)
    student = result["student"]
    print(
        f"\nRecommendations for {student['student_name']} "
        f"({student['department_name']}, year {student['year_level']}, GPA {student['gpa']:.2f}):"
    )
    if not result["recommendations"]:
        print("No eligible courses found.")
    for course in result["recommendations"]:
        print(
            f"\n{course['course_id']} - {course['course_name']} "
            f"(score {course['score']}, {course['credits']} credits)"
        )
        print(f"  Why: {course['reason']}")
    print(f"\nNote: {result['note']}")

def run_academic_analytics(student_id):
    analytics = AcademicAnalytics(data_dir=ROOT / "uni_assist_dataset")
    analytics.print_report(student_id)

def read_temperature(default=0.5):
    selection = input(f"Temperature 0-1 [{default}]: ").strip()
    if not selection:
        return default
    try:
        temperature = float(selection)
    except ValueError:
        print("Invalid number; using the default temperature.")
        return default
    if not 0 <= temperature <= 1:
        print("Temperature must be between 0 and 1; using the default.")
        return default
    return temperature


def chat_session(temperature=0.5):
    from helper import send_gptnew

    temperature = read_temperature(temperature)
    print("\nType /back to return to the menu.")
    while True:
        try:
            question = input("\nYou: ").strip()
        except EOFError:
            print()
            return
        if question.casefold() in {"/back", "/quit", "exit"}:
            return
        if not question:
            continue
        try:
            answer = send_gptnew(question, temperature)
        except LocalLLMError as error:
            answer = str(error)
        print(f"\nChatbot: {answer}")


def run_interactive():
    while True:
        print("\nAI-Powered Educational Chatbot")
        print("1. Chat")
        print("2. Course recommendations")
        print("3. Academic Analytics")
        print("4. Exit")
        try:
            choice = input("Select an option: ").strip()
        except EOFError:
            print()
            return 0

        if choice == "1":
            chat_session()
        elif choice == "2":
            student_id = input("Student ID (for example S0001): ").strip()
            count = input("Number of recommendations [5]: ").strip()
            try:
                top_n = max(1, min(int(count) if count else 5, 10))
                recommend_courses(student_id, top_n)
            except ValueError as error:
                print(f"Could not recommend courses: {error}")

        elif choice == "3":
            student_id = input("Student ID (for example S0001): ").strip()
            try:
                run_academic_analytics(student_id)
            except (ValueError, FileNotFoundError) as error:
                print(f"Could not analyze student: {error}")

        elif choice == "4":
            return 0

        else:
            print("Choose 1, 2, 3, or 4.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Terminal-based educational chatbot")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--ask", metavar="QUESTION", help="Ask one question and exit")
    mode.add_argument("--recommend", metavar="STUDENT_ID", help="Recommend courses and exit")
    parser.add_argument("--temperature", type=float, default=0.5)
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args(argv)

    if not 0 <= args.temperature <= 1:
        parser.error("--temperature must be between 0 and 1")
    if args.ask is not None:
        try:
            from helper import send_gptnew

            print(send_gptnew(args.ask, args.temperature))
        except LocalLLMError as error:
            print(error)
            return 1
        return 0
    if args.recommend is not None:
        try:
            recommend_courses(args.recommend, max(1, min(args.top_n, 10)))
        except ValueError as error:
            print(f"Could not recommend courses: {error}")
            return 1
        return 0
    return run_interactive()


if __name__ == "__main__":
    raise SystemExit(main())
