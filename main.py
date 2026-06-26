from datetime import date 
import pandas as pd  # pip install pandas
# from deta import app
from send_email import send_email
import datetime
from datetime import datetime


# not secure
SHEET_ID = "1X9R5q-tXTkYjDjdoggGQkL1Cc7BLZcu6Fy8A3JHnJk4" 
# SHEET_NAME = "Birthday_Sheet"
month_text = datetime.now().strftime("%B")
if (month_text) :
    SHEET_NAME = month_text

URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"


def load_df(url):
    parse_dates = ["Birthday"]
    df = pd.read_csv(url, parse_dates=parse_dates)
    return df


def query_data_and_send_emails(df):
    present = date.today()
    email_counter = 0
    for _, row in df.iterrows():
        if (present = row["Birthday"].date()):
            send_email(
                subject=f'Happy Birthday!!',
                receiver_email=row["Email"],
                name=row["Name"],
                birthday_date=row["Birthday"].strftime("%d, %b %Y"),  # 22, Aug 2023
            )
            email_counter += 1
    return f"Total Emails Sent: {email_counter}"


df = load_df(URL)
result = query_data_and_send_emails(df)
print(result)

# @app.lib.cron()
# def cron_job(event):
#     df = load_df(URL)
#     result = query_data_and_send_emails(df)
#     return result
