from apscheduler.schedulers.background import BackgroundScheduler
from certificate_utils import get_cert_expiry
from email_utils import send_email
from database import get_db_connection
from datetime import datetime
from config import (
    CERT_ALERT_DAYS_BEFORE,
    LICENSE_ALERT_DAYS_BEFORE,
    CERT_CHECK_TIME,
    ALERT_SEND_TIME
)
from logger import logger

def parse_time(time_str):
    hour, minute = map(int, time_str.split(":"))
    return hour, minute

def check_cert_expiry():
    logger.info("Running certificate expiry check...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, url FROM services")
    services = cursor.fetchall()
    for service_id, name, url in services:
        try:
            expiry_date = get_cert_expiry(url)
            cursor.execute(
                "UPDATE services SET certificate_expiry = ? WHERE id = ?",
                (expiry_date.strftime("%Y-%m-%d"), service_id)
            )
            logger.info(f"Updated certificate expiry for {name} ({url}): {expiry_date}")
        except Exception as e:
            logger.error(f"Error checking certificate for {url}: {e}")
    conn.commit()
    conn.close()

def send_alerts():
    logger.info("Sending alerts...")
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.utcnow().date()

    cursor.execute("SELECT name, expiry_date, alert_email FROM licenses")
    for name, expiry_str, emails in cursor.fetchall():
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        if 0 <= (expiry_date - today).days <= LICENSE_ALERT_DAYS_BEFORE:
            subject = f"License Expiry Warning: {name}"
            body = f"The license '{name}' is expiring on {expiry_date}."
            send_email(emails.split(","), subject, body)
            logger.info(f"Alert email sent for license: {name} → {emails}")

    cursor.execute("SELECT name, certificate_expiry, alert_email FROM services")
    for name, expiry_str, emails in cursor.fetchall():
        if expiry_str:
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            if 0 <= (expiry_date - today).days <= CERT_ALERT_DAYS_BEFORE:
                subject = f"Certificate Expiry Warning: {name}"
                body = f"The SSL certificate for '{name}' is expiring on {expiry_date}."
                send_email(emails.split(","), subject, body)
                logger.info(f"Alert email sent for certificate: {name} → {emails}")
    conn.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    cert_hour, cert_minute = parse_time(CERT_CHECK_TIME)
    scheduler.add_job(check_cert_expiry, 'cron', hour=cert_hour, minute=cert_minute)

    alert_hour, alert_minute = parse_time(ALERT_SEND_TIME)
    scheduler.add_job(send_alerts, 'cron', hour=alert_hour, minute=alert_minute)

    scheduler.start()
