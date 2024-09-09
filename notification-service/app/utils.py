import smtplib
from email.mime.text import MIMEText
from sqlmodel import Session

async def send_email(user_id: int, message: str):        
    sender_email = 'aq98123@gmail.com'
    recipient_email = 'abdulqadarmayo786@gmail.com'
    subject = "Notification from FastAPI Notification App"

    # Create the email content
    msg = MIMEText(message, 'plain')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Send email via SMTP
    smtp_server = 'smtp.gmail.com'  # Replace with your SMTP server
    smtp_port = 587
    smtp_username = 'aq98123@gmail.com'
    smtp_password = 'ttba ybjs xels ofof'

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure connection
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise
