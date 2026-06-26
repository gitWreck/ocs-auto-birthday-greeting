import os, random, json
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid, formataddr
from pathlib import Path

from dotenv import load_dotenv  # pip install python-dotenv

PORT = 587
EMAIL_SERVER = "smtp.gmail.com"  # Adjust server address

# Load the environment variables
current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = current_dir / ".env"
load_dotenv(envars)

# Read environment variables
sender_email = os.getenv("EMAIL")
password_email = os.getenv("PASSWORD")

# Load birthday phrases
phrases_path = current_dir / "birthday_phrases.json"
try:
    with open(phrases_path, "r", encoding="utf-8") as f:
        phrases_data = json.load(f)
except Exception:
    phrases_data = {
        "body_phrases": ["Today, we celebrate YOU!"],
        "closing_phrases": ["Have a very happy birthday!"]
    }


def send_email(subject, receiver_email, name, birthday_date, is_student=False):
    if not sender_email or not password_email:
        raise ValueError(
            "EMAIL or PASSWORD environment variables are not set. "
            "Please check your .env file in the root folder."
        )

    # Create the base text message.

    # # Add the html version.  This converts the message into a multipart/alternative

    # print(current_dir)
    # print(password_email)
    gif_dir = '/home/cfnrocs0118/ocs_auto_birthday_greeting/birthday_gif/'
    if not os.path.exists(gif_dir):
        gif_dir = os.path.join(current_dir, 'birthday_gif')

    body_phrases = phrases_data.get("body_phrases", ["Today, we celebrate YOU!"])
    closing_phrases = phrases_data.get("closing_phrases", ["Have a very happy birthday!"])

    CBody = random.choice(body_phrases)
    selected_closing = random.choice(closing_phrases)

    if is_student:
        card_header_color = '#0c513e'
        if "birthday!" in selected_closing.lower():
            CRem = selected_closing.replace("birthday!", f"birthday, {name.title()}!")
        elif "birthday" in selected_closing.lower():
            CRem = selected_closing.replace("birthday", f"birthday, {name.title()}")
        else:
            CRem = f"{selected_closing} Have a very happy birthday, {name.title()}!"
    else:
        card_header_color = '#90143c'
        CRem = selected_closing

    msg = EmailMessage()
    msg["Subject"] = subject + " " + name.title() + "!"
    msg["From"] = formataddr(("Office of the College Secretary CFNR UP Los Banos", f"{sender_email}"))
    msg["To"] = receiver_email

    gifs = os.listdir(gif_dir)
    r = random.choice(gifs)

    attachment = os.path.join(gif_dir, r)
    attachment_cid = make_msgid()

    GLabel = f"Dear {name.title()},"
    CBody = "Today, we celebrate YOU!"
    msg.set_content(
        '''
        <head>
        <style>
        body {
          background-color: linen;
          margin-left: 20px;
        }

        h1 {
          color: #426839;
          font-family: monospace;
          text-transform: uppercase;
          word-spacing: -4px;
        }
        p {
          color: #333;
          font-size: 20px;
          text-transform: uppercase;
          font-family: "Lucida Console", "Courier New", monospace;
          word-spacing: -4px;
        }
        img {
            width: 550px;
            height: 421px;
            border-radius: 10px;
        }
        .card-container {
            background-color: #f7eed5;
            border-radius: 20px;
            display: flex;
        }
        .card-header {
            background-color: %s;
            border-radius: 15px 0px 0px 15px;
            padding: 20px;
            width: 30px;
            background-image: url("https://firebasestorage.googleapis.com/v0/b/image-storage-70862.appspot.com/o/balloon_resize.png?alt=media&token=363d3b21-9cc0-4319-94fe-7079dbbd639a");
            background-repeat: repeat;
        }
        .card-content {
            padding-left: 10px;
            padding-left: 10px;
        }
        </style>
        </head>
        <body>
            <div class="card-container">
                <div class="card-header">
                </div>
                <div class="card-content">
                    <h1>%s</h1>
                    <p>%s</p>
                        <img src="cid:%s" alt="Birthday GIF"/>
                    <p>%s</p>
                </div>
            </div>
        </body>
        ''' % (card_header_color, GLabel, CBody, attachment_cid[1:-1], CRem), 'html')

    with open(attachment, 'rb') as fp:
        msg.add_related(
            fp.read(), 'image', 'gif', cid=attachment_cid, filename='Happy Birthday.gif')

    # print(msg.as_string())

    with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
        server.starttls()
        server.login(sender_email, password_email)
        server.sendmail(sender_email, receiver_email, msg.as_string())


if __name__ == "__main__":
    send_email(
        subject="Happy Birthday",
        name="FedGde",
        receiver_email="aesplanabedtc@gmail.com",
        birthday_date="22, Aug 2023",
    )
