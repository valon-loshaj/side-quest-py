import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.side_quest_py.celery_app import celery_app
from src.side_quest_py.database import SessionLocal
from src.side_quest_py.models.db_models import User, Adventurer
from src.side_quest_py.api.config import settings


class EmailSendError(Exception):
    """Exception raised when an email fails to send."""

    pass


@celery_app.task
def send_level_up_email(adventurer_id: str, old_level: int, new_level: int):
    """
    Send a level-up notification email to the user.

    Args:
        adventurer_id: ID of the adventurer who leveled up
        old_level: Previous level
        new_level: New level after leveling up
    """
    db = SessionLocal()
    try:
        # Get adventurer with user info
        adventurer = db.query(Adventurer).filter(Adventurer.id == adventurer_id).first()
        if not adventurer:
            return f"Adventurer {adventurer_id} not found"

        # Get the user
        user = db.query(User).filter(User.id == adventurer.user_id).first()
        if not user:
            return f"User for adventurer {adventurer_id} not found"

        # Create email content
        subject = f"Your adventurer {adventurer.name} has reached level {new_level}!"

        if new_level % 5 == 0:  # Special message for milestone levels
            body = f"""
            <html>
            <body>
            <h2>🎉 MAJOR MILESTONE ACHIEVED! 🎉</h2>
            <p>Congratulations, brave hero!</p>
            <p>Your adventurer <strong>{adventurer.name}</strong> has achieved the impressive rank of <strong>Level {new_level}</strong>!</p>
            <p>This is a significant milestone in your journey. New quests, abilities, and challenges await!</p>
            <p>Return to Side Quest to see what new opportunities have unlocked.</p>
            </body>
            </html>
            """
        else:
            body = f"""
            <html>
            <body>
            <h2>Level Up!</h2>
            <p>Congratulations!</p>
            <p>Your adventurer <strong>{adventurer.name}</strong> has advanced from Level {old_level} to <strong>Level {new_level}</strong>.</p>
            <p>Continue your heroic journey at Side Quest!</p>
            </body>
            </html>
            """

        # Send the email
        send_email(str(user.email), subject, body)

        return f"Level up email sent to {str(user.email)} for adventurer {adventurer.name}"
    except EmailSendError as e:
        return f"Error sending email: {e}"
    finally:
        db.close()


def send_email(to_email: str, subject: str, html_body: str):
    """Helper function to send an email.

    Args:
        to_email: Email address to send the email to
        subject: Subject of the email
        html_body: HTML body of the email

    Returns:
        str: Message indicating the email was sent successfully
    """
    # Email configuration
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    smtp_username = settings.SMTP_USERNAME
    smtp_password = settings.SMTP_PASSWORD
    from_email = settings.SMTP_SENDER_EMAIL

    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Attach HTML content
    html_part = MIMEText(html_body, "html")
    msg.attach(html_part)

    # For development
    print(f"\n==== EMAIL WOULD BE SENT ====")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {html_body}")
    print(f"==== END OF EMAIL ====\n")

    # Uncomment to actually send emails when properly configured
    # with smtplib.SMTP(smtp_server, smtp_port) as server:
    #     server.starttls()
    #     server.login(smtp_username, smtp_password)
    #     server.send_message(msg)
