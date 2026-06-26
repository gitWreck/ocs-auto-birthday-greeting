from datetime import datetime
from urllib.parse import quote
import pandas as pd
import main_faculty
import main_students
from send_email import send_email

TEST_SHEET_NAME = "Test"

FACULTY_TEST_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{main_faculty.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(TEST_SHEET_NAME)}"
)

STUDENTS_TEST_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{main_students.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(TEST_SHEET_NAME)}"
)

def clean_val(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

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
            for _, row in df_today.iterrows():
                address_as = clean_val(row.get("AD")) if clean_val(row.get("AD")) else clean_val(row.get("DESIGNATION"))
                name = clean_val(row.get("NICKNAME")) if clean_val(row.get("NICKNAME")) else clean_val(row.get("FIRSTNAME"))
                final_name = f"{address_as} {name}".strip()
                email = clean_val(row.get("Email"))
                if email:
                    print(f"Sending test email to Faculty: {email}...")
                    send_email(
                        subject="Happy Birthday!",
                        receiver_email=email,
                        name=final_name,
                        birthday_date=row["Birthday"].strftime("%d %b %Y"),
                        is_student=False
                    )
                    print("Sent successfully!")
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
            for _, row in df_today.iterrows():
                email = clean_val(row.get("Email"))
                if email:
                    print(f"Sending test email to Student: {email}...")
                    send_email(
                        subject="Happy Birthday,",
                        receiver_email=email,
                        name=row["Name"],
                        birthday_date=row["Birthday"].strftime("%d %b %Y"),
                        is_student=True
                    )
                    print("Sent successfully!")
        else:
            print("None.")
    except Exception as e:
        print(f"Error testing Students sheet: {e}")

if __name__ == "__main__":
    test_faculty()
    test_students()