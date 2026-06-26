import argparse

import main_faculty
import main_students

def run_faculty():
    print("=== STARTING FACULTY BIRTHDAY CHECK ===")
    try:
        faculty_df = main_faculty.load_df(main_faculty.URL)
        faculty_result = main_faculty.query_data_and_send_emails(faculty_df)
        print(f"Faculty Result: {faculty_result}")
    except Exception as e:
        print(f"Error running faculty birthdays: {e}")

def run_students():
    print("=== STARTING STUDENTS BIRTHDAY CHECK ===")
    try:
        student_df = main_students.load_df(main_students.URL)
        student_result = main_students.query_data_and_send_emails(student_df)
        print(f"Students Result: {student_result}")
    except Exception as e:
        print(f"Error running students birthdays: {e}")

def main():
    parser = argparse.ArgumentParser(description="Auto Birthday Greetings Runner")
    parser.add_argument(
        "--type",
        choices=["faculty", "students", "both"],
        default="both",
        help="Specify whether to run faculty, students, or both (default: both)"
    )
    args = parser.parse_args()

    if args.type in ("faculty", "both"):
        run_faculty()
    
    if args.type in ("students", "both"):
        run_students()

if __name__ == "__main__":
    main()