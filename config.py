EMAIL_SENDER = 'notify@example.com'
EMAIL_PASSWORD = '[password]'
SMTP_SERVER = 'mail.example.com'
SMTP_PORT = 465  # 465 for SSL, 587 for TLS
USE_SSL = True  # True = use SSL, False = use TLS

# Certificate Check Time (24-hour format)
CERT_CHECK_TIME = "09:00"
ALERT_SEND_TIME = "14:46"

# Alert thresholds
CERT_ALERT_DAYS_BEFORE = 7
LICENSE_ALERT_DAYS_BEFORE = 10

JWT_SECRET = 'your-jwt-secret-key'
