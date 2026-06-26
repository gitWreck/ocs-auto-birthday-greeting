from datetime import date, datetime
from urllib.parse import quote

import pandas as pd
from send_email import send_email

SHEET_ID = "1X9R5q-tXTkYjDjdoggGQkL1Cc7BLZcu6Fy8A3JHnJk4"
SHEET_NAME = datetime.now().strftime("%B")

URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(SHEET_NAME)}"
)


def load_df(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # Keep only the first 5 columns
    df = df.iloc[:, :5]

    # If your sheet has NO headers, use this:
    df.columns = ["Last", "Name", "Middle", "Email", "Birthday"]

    first_names = df["Name"].fillna("").astype(str).str.strip()
    last_names = df["Last"].fillna("").astype(str).str.strip()
    df["Name"] = (first_names + " " + last_names).str.strip()

    # Accepts 5/1/2001, 05/01/2001, 5-1-2001, etc.
    df["Birthday"] = pd.to_datetime(
        df["Birthday"],
        format="mixed",
        errors="coerce"
    )

    return df


def query_data_and_send_emails(df: pd.DataFrame) -> str:
    today_md = date.today().strftime("%m-%d")
    email_counter = 0

    df_today = df[
        df["Birthday"].notna()
        & (df["Birthday"].dt.strftime("%m-%d") == today_md)
    ]

    print("Birthdays today:")
    print(df_today[["Name", "Email", "Birthday"]])

    for _, row in df_today.iterrows():
        email = str(row.get("Email", "")).strip() if pd.notna(row.get("Email")) else ""
        name = str(row.get("Name", "")).strip()

        if not email or "@" not in email:
            print(f"Skipped student {name}: no valid email address")
            continue

        send_email(
            subject="Happy Birthday,",
            receiver_email=email,
            name=name,
            birthday_date=row["Birthday"].strftime("%d %b %Y"),
            is_student=True,
        )

        email_counter += 1
        print(f"Sent birthday email to {email}")

    return f"Total Emails Sent: {email_counter}"


if __name__ == "__main__":
    df = load_df(URL)
    result = query_data_and_send_emails(df)
    print(result)
