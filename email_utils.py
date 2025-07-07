import smtplib
import logging
from email.mime.text import MIMEText
from config import (
    EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT, USE_SSL
)

def send_email(recipients, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = ', '.join(recipients)

    try:
        if USE_SSL:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, recipients, msg.as_string())
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, recipients, msg.as_string())

        logging.info(f"Email sent to {recipients}")
    except Exception as e:
        logging.error(f"Email error: {e}")
