from datetime import datetime, timedelta
from collections import defaultdict

# import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.side_quest_py.celery_app import celery_app
from src.side_quest_py.database import SessionLocal
from src.side_quest_py.models.db_models import User, Adventurer, Quest, QuestCompletion
from src.side_quest_py.api.config import settings


class EmailSendError(Exception):
    """Exception raised when an email fails to send."""


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


@celery_app.task
def send_daily_recap_emails():
    """
    Generate and send daily recap emails to all users.
    This task should be scheduled to run once per day.
    """
    db = SessionLocal()
    try:
        # Calculate yesterday's date range
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today - timedelta(days=1)
        yesterday_end = today

        # Get all quest completions from yesterday with related data
        completions = (
            db.query(QuestCompletion, Quest, Adventurer)
            .join(Quest, QuestCompletion.quest_id == Quest.id)
            .join(Adventurer, QuestCompletion.adventurer_id == Adventurer.id)
            .filter(QuestCompletion.created_at >= yesterday_start, QuestCompletion.created_at < yesterday_end)
            .all()
        )

        # Group completions by user
        user_completions = defaultdict(lambda: defaultdict(list))

        for completion, quest, adventurer in completions:
            user_id = adventurer.user_id
            user_completions[user_id][adventurer.id].append((quest, completion))

        # Send recap email to each user who had activity
        for user_id, adventurer_completions in user_completions.items():
            # Get user info
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                continue

            # Generate and send the email
            send_user_daily_recap(user, adventurer_completions, yesterday_start.date())

        return f"Daily recap emails sent to {len(user_completions)} users"
    finally:
        db.close()


def send_user_daily_recap(user, adventurer_completions, recap_date):
    """
    Send a daily recap email to a specific user.

    Args:
        user: User object with email and username
        adventurer_completions: Dict mapping adventurer_id to list of (quest, completion) tuples
        recap_date: The date of the activity being recapped
    """
    db = SessionLocal()
    try:
        # Get adventurer details
        adventurer_ids = list(adventurer_completions.keys())
        adventurers = {adv.id: adv for adv in db.query(Adventurer).filter(Adventurer.id.in_(adventurer_ids)).all()}

        # Format date for email
        formatted_date = recap_date.strftime("%A, %B %d, %Y")

        # Calculate overall stats
        total_quests = sum(len(quests) for quests in adventurer_completions.values())
        total_xp = sum(
            quest.experience_reward for adv_quests in adventurer_completions.values() for quest, _ in adv_quests
        )

        # Create email subject and intro
        subject = f"Your Side Quest Daily Recap for {formatted_date}"

        # Start building HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h1 style="color: #4b6584;">Daily Quest Recap</h1>
            <p>Hello {user.username},</p>
            <p>Here's your daily adventure summary for <strong>{formatted_date}</strong>:</p>
            
            <div style="background-color: #f7f7f7; padding: 10px; border-radius: 5px; margin: 15px 0;">
                <h3 style="margin-top: 0; color: #3867d6;">Overall Progress</h3>
                <p>Total Quests Completed: <strong>{total_quests}</strong></p>
                <p>Total Experience Gained: <strong>{total_xp} XP</strong></p>
            </div>
        """

        # Add details for each adventurer
        for adventurer_id, quests_info in adventurer_completions.items():
            adventurer = adventurers.get(adventurer_id)
            if not adventurer:
                continue

            # Calculate adventurer-specific stats
            adv_xp = sum(quest.experience_reward for quest, _ in quests_info)

            html_content += f"""
            <div style="margin-bottom: 20px; border-left: 4px solid #3867d6; padding-left: 15px;">
                <h2 style="color: #3867d6; margin-bottom: 10px;">{adventurer.name} (Level {adventurer.level})</h2>
                <p>Quests Completed: <strong>{len(quests_info)}</strong></p>
                <p>Experience Gained: <strong>{adv_xp} XP</strong></p>
                
                <ul style="list-style-type: none; padding-left: 0;">
            """

            # List each quest completed by this adventurer
            for quest, completion in quests_info:
                # Format completion time
                completion_time = completion.created_at.strftime("%I:%M %p")

                html_content += f"""
                <li style="padding: 8px; margin-bottom: 8px; background-color: #f1f2f6; border-radius: 4px;">
                    <div style="font-weight: bold;">{quest.title}</div>
                    <div style="color: #576574; font-size: 0.9em;">Completed at {completion_time}</div>
                    <div style="color: #20bf6b; font-size: 0.9em;">+{quest.experience_reward} XP</div>
                </li>
                """

            html_content += """
                </ul>
            </div>
            """

        # Add footer
        html_content += """
            <p>Keep up the great adventuring!</p>
            <p>The Side Quest Team</p>
        </body>
        </html>
        """

        # Send the email
        send_email(user.email, subject, html_content)

        return f"Daily recap email sent to {user.email}"
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
    # smtp_server = settings.SMTP_SERVER
    # smtp_port = settings.SMTP_PORT
    # smtp_username = settings.SMTP_USERNAME
    # smtp_password = settings.SMTP_PASSWORD
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
