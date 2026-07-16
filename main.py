import argparse
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import pandas as pd
from send_email import send_email, log_activity

PHT = timezone(timedelta(hours=8))

# Google Sheets IDs
FACULTY_SHEET_ID = "1booIk3Kj31kK3pwMV7Ga7vMKja7_0IYd_jMMzy5lsTk"
STUDENTS_SHEET_ID = "1X9R5q-tXTkYjDjdoggGQkL1Cc7BLZcu6Fy8A3JHnJk4"


def clean_value(value, fallback=""):
    if pd.isna(value):
        return fallback
    value = str(value).strip()
    return fallback if value == "" else value


def pick_value(primary, fallback):
    primary = clean_value(primary)
    fallback = clean_value(fallback)
    return primary if primary else fallback


def load_faculty_df(sheet_name: str) -> pd.DataFrame:
    url = (
        f"https://docs.google.com/spreadsheets/d/{FACULTY_SHEET_ID}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(sheet_name)}&headers=1"
    )
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()

    # Map alternative column names if necessary
    rename_map = {}
    if "Birthday" not in df.columns and "DOB" in df.columns:
        rename_map["DOB"] = "Birthday"
    elif "Birthday" not in df.columns and "BIRTH DATE" in df.columns:
        rename_map["BIRTH DATE"] = "Birthday"
        
    if "Email" not in df.columns and "EMAIL" in df.columns:
        rename_map["EMAIL"] = "Email"
        
    if rename_map:
        df = df.rename(columns=rename_map)

    required_columns = [
        "DESIGNATION",
        "DEPARTMENT",
        "AD",
        "NICKNAME",
        "FIRSTNAME",
        "Birthday",
        "Email",
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Faculty sheet missing required columns: {missing_columns}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    df["Birthday"] = pd.to_datetime(df["Birthday"], format="mixed", errors="coerce")
    return df


def load_students_df(sheet_name: str) -> pd.DataFrame:
    url = (
        f"https://docs.google.com/spreadsheets/d/{STUDENTS_SHEET_ID}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(sheet_name)}&headers=1"
    )
    df = pd.read_csv(url)
    df = df.iloc[:, :5]  # Keep only the first 5 columns
    df.columns = ["Last", "Name", "Middle", "Email", "Birthday"]

    first_names = df["Name"].fillna("").astype(str).str.strip()
    last_names = df["Last"].fillna("").astype(str).str.strip()
    df["Name"] = (first_names + " " + last_names).str.strip()

    df["Birthday"] = pd.to_datetime(df["Birthday"], format="mixed", errors="coerce")
    return df


def run_birthday_check(is_student: bool, sheet_name: str):
    label = "STUDENT" if is_student else "FACULTY"
    print(f"=== STARTING {label} BIRTHDAY CHECK ({sheet_name}) ===")

    try:
        if is_student:
            df = load_students_df(sheet_name)
        else:
            df = load_faculty_df(sheet_name)

        today_md = datetime.now(PHT).strftime("%m-%d")
        df_today = df[
            df["Birthday"].notna()
            & (df["Birthday"].dt.strftime("%m-%d") == today_md)
        ]

        print("Birthdays today:")
        name_col = "Name" if is_student else "FIRSTNAME"
        if len(df_today) > 0 and name_col in df_today.columns:
            print(df_today[[name_col, "Email", "Birthday"]])
        else:
            print("None.")

        email_counter = 0
        for _, row in df_today.iterrows():
            if is_student:
                name = str(row.get("Name", "")).strip()
                subject = "Happy Birthday,"
            else:
                address_as = pick_value(row.get("AD"), row.get("DESIGNATION"))
                nick_or_first = pick_value(row.get("NICKNAME"), row.get("FIRSTNAME"))
                name = f"{address_as} {nick_or_first}".strip()
                subject = "Happy Birthday!"

            email = clean_value(row.get("Email"))
            if not email or (is_student and "@" not in email):
                print(f"Skipped {label.lower()} {name}: no valid email address")
                continue

            try:
                send_email(
                    subject=subject,
                    receiver_email=email,
                    name=name,
                    birthday_date=row["Birthday"].strftime("%d %b %Y"),
                    is_student=is_student,
                )
                email_counter += 1
                print(f"Sent birthday email to {email}")
            except Exception as email_err:
                print(f"Failed to send email to {name} ({email}): {email_err}")

        log_activity(f"[{label}] Check completed. Total Emails Sent: {email_counter}")
        print(f"{label} Result: Total Emails Sent: {email_counter}")

    except Exception as e:
        print(f"Error running {label.lower()} birthdays: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Auto Birthday Greetings Runner (Caveman Lite Edition)"
    )
    parser.add_argument(
        "--type",
        choices=["faculty", "students", "both"],
        default="both",
        help="Specify whether to run faculty, students, or both (default: both)",
    )
    args = parser.parse_args()

    sheet_name = datetime.now(PHT).strftime("%B")
    print(f"Using sheet/tab: {sheet_name}")

    if args.type in ("faculty", "both"):
        run_birthday_check(is_student=False, sheet_name=sheet_name)

    if args.type in ("students", "both"):
        run_birthday_check(is_student=True, sheet_name=sheet_name)


if __name__ == "__main__":
    main()