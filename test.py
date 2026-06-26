import os, random, sys
from email.message import EmailMessage
from email.utils import make_msgid

msg = EmailMessage()
msg["To"] = "to_addr"
msg["From"] = "from_addr"
msg["Subject"] = "subject"

gifs = os.listdir('birthday_gif/')
r = random.choice(gifs)

attachment = 'birthday_gif/' + r
attachment_cid = make_msgid()

body = f"""\
      <body>
        <p>Dear Test: </p>
        <p>TODAY, we celebrate YOU!<p/>
      </body>
    """

msg.set_content(
    '<b>%s</b><br/><img src="cid:%s"/><br/>' % (
        body, attachment_cid[1:-1]), 'html')

with open(attachment, 'rb') as fp:
    msg.add_related(
        fp.read(), 'image', 'gif', cid=attachment_cid)

print(msg.as_string())