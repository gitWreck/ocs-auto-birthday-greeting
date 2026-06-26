from datetime import datetime
from urllib.parse import quote
import main_faculty
import main_students

TEST_SHEET_NAME = "Test"

FACULTY_TEST_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{main_faculty.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(TEST_SHEET_NAME)}"
)

STUDENTS_TEST_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{main_students.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(TEST_SHEET_NAME)}"
)

def test_faculty():
    print("====================================")
    print(f"TESTING FACULTY SHEET LOAD ({TEST_SHEET_NAME})")
    print("====================================")
    try:
        df = main_faculty.load_df(FACULTY_TEST_URL)
        print(f"Success! Loaded {len(df)} rows from Faculty sheet.")
        print(f"Columns found: {df.columns.tolist()}")
        print("\nFirst 3 rows:")
        print(df.head(3))
        
        # Test today's birthdays lookup
        today_md = datetime.now().strftime("%m-%d")
        df_today = df[
            df["Birthday"].notna()
            & (df["Birthday"].dt.strftime("%m-%d") == today_md)
        ]
        print(f"\nBirthdays found for today ({today_md}):")
        if len(df_today) > 0:
            print(df_today[["FIRSTNAME", "NICKNAME", "Email", "Birthday"]])
        else:
            print("None.")
    except Exception as e:
        print(f"Error testing Faculty sheet: {e}")

def test_students():
    print("\n====================================")
    print(f"TESTING STUDENTS SHEET LOAD ({TEST_SHEET_NAME})")
    print("====================================")
    try:
        df = main_students.load_df(STUDENTS_TEST_URL)
        print(f"Success! Loaded {len(df)} rows from Students sheet.")
        print(f"Columns found: {df.columns.tolist()}")
        print("\nFirst 3 rows:")
        print(df.head(3))
        
        # Test today's birthdays lookup
        today_md = datetime.now().strftime("%m-%d")
        df_today = df[
            df["Birthday"].notna()
            & (df["Birthday"].dt.strftime("%m-%d") == today_md)
        ]
        print(f"\nBirthdays found for today ({today_md}):")
        if len(df_today) > 0:
            print(df_today[["Name", "Email", "Birthday"]])
        else:
            print("None.")
    except Exception as e:
        print(f"Error testing Students sheet: {e}")

if __name__ == "__main__":
    test_faculty()
    test_students()