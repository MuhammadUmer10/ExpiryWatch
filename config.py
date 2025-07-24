SERVER_PORT = 5001

EMAIL_SENDER = 'notify@example.com'
EMAIL_PASSWORD = 'SMTPPASSWORD'
SMTP_SERVER = 'mail.example.com'
SMTP_PORT = 465  # 465 for SSL, 587 for TLS
USE_SSL = True  # True = use SSL, False = use TLS

# Certificate Check Time (24-hour format)
CERT_CHECK_TIME = "10:00"
ALERT_SEND_TIME = "14:00"

# Alert thresholds
CERT_ALERT_DAYS_BEFORE = 10
LICENSE_ALERT_DAYS_BEFORE = 10

JWT_SECRET = 'your-jwt-secret-key'
