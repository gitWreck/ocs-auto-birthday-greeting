import os, random
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
if not envars.exists():
    envars = current_dir.parent / ".env"
load_dotenv(envars)

# Read environment variables
sender_email = os.getenv("EMAIL")
password_email = os.getenv("PASSWORD")


def send_email(subject, receiver_email, name, birthday_date):
    # Create the base text message.

    # # Add the html version.  This converts the message into a multipart/alternative
    # background-color: #c1faa0; card-header

    msg = EmailMessage()
    msg["Subject"] = subject + " " + name.title() + "!"
    msg["From"] = formataddr(("Office of the College Secretary CFNR UP Los Banos", f"{sender_email}"))
    msg["To"] = receiver_email

    gifs = os.listdir('/home/aesplana31/Birthday_Greeting/birthday_gif/')
    r = random.choice(gifs)

    attachment = '/home/aesplana31/Birthday_Greeting/birthday_gif/' + r
    attachment_cid = make_msgid()

    GLabel = f"Dear {name.title()},"
    CBody = "Today, we celebrate YOU!"
    CRem = f"Have a very happy birthday, {name.title()}!"
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
        }
        p {
          color: #333;
          font-size: 20px;
          text-transform: uppercase;
          font-family: "Lucida Console", "Courier New", monospace;
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
            background-color: #0c513e;
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
        ''' % (GLabel, CBody,attachment_cid[1:-1], CRem), 'html')

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
