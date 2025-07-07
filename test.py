import smtplib

server = smtplib.SMTP_SSL('mail.dictalabs.com', 465)
server.login("notify@dictalabs.com", "s%rXxcDZW,^A")  # <- special chars here
print("Login successful")