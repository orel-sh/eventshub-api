from celery import Celery
from app.config.settings import settings
import smtplib
from email.mime.text import MIMEText

celery_app = Celery(
    "geoevents",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"


@celery_app.task(name="send_registration_confirmation")
def send_registration_confirmation(to_email: str, user_name: str, event_title: str, event_date: str):
    subject = f"Registration Confirmed: {event_title}"
    body = f"""Hi {user_name},

You have successfully registered for: {event_title}
Date: {event_date}

See you there!
GeoEvents Team
"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except Exception as e:
        # Log and continue — email failure should not block the API
        print(f"[Email Error] {e}")
