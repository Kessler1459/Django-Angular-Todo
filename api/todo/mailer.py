import smtplib, ssl
from .enviroment import MY_ENV_VAR
sender_email="kessler1459@gmail.com"
port = 465  # For SSL
password = MY_ENV_VAR

def sendEmail(message:str,to:str):
# Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(from_addr=sender_email,to_addrs=to,msg=message)