from datetime import date, datetime
from urllib.parse import quote

import pandas as pd
from send_email import send_email

SHEET_ID = "1booIk3Kj31kK3pwMV7Ga7vMKja7_0IYd_jMMzy5lsTk"
SHEET_NAME = datetime.now().strftime("%B")

print("Using sheet:", SHEET_NAME)

URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote(SHEET_NAME)}"
)

def clean_value(value, fallback=""):
    if pd.isna(value):
        return fallback

    value = str(value).strip()

    if value == "":
        return fallback

    return value


def pick_value(primary, fallback):
    primary = clean_value(primary)
    fallback = clean_value(fallback)

    return primary if primary else fallback


def load_df(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # Clean column names
    df.columns = df.columns.str.strip()

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
            f"Missing required columns: {missing_columns}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    # Supports: 5/9/2007, 05/09/2007, 5-9-2007, etc.
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
    print(df_today[["FIRSTNAME", "NICKNAME", "Email", "Birthday"]])

    for _, row in df_today.iterrows():
        address_as = pick_value(row.get("AD"), row.get("DESIGNATION"))
        name = pick_value(row.get("NICKNAME"), row.get("FIRSTNAME"))

        final_name = f"{address_as} {name}".strip()

        email = clean_value(row.get("Email"))

        if not email:
            print(f"Skipped {final_name}: no email address")
            continue

        send_email(
            subject="Happy Birthday!",
            receiver_email=email,
            name=final_name,
            birthday_date=row["Birthday"].strftime("%d %b %Y"),
        )

        email_counter += 1
        print(f"Sent birthday email to {email}")

    return f"Total Emails Sent: {email_counter}"


if __name__ == "__main__":
    df = load_df(URL)
    result = query_data_and_send_emails(df)
    print(result)
