import smtplib
from email.mime.text import MIMEText

EMAIL = "narun7744@gmail.com"
APP_PASSWORD = "cajx rsay krvz utdf"

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL, APP_PASSWORD)

msg = MIMEText("This is a test email.")
msg["Subject"] = "SMTP Test"
msg["From"] = EMAIL
msg["To"] = EMAIL

server.send_message(msg)
server.quit()

print("Email sent successfully!")