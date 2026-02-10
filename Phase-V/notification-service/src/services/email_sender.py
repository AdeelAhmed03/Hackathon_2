"""Email notification sender.

T066: Send email notifications for task reminders.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger("notification-service.services.email")

# Email configuration (from environment/secrets)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@todo-app.local")


async def send_email_notification(
    user_id: str,
    subject: str,
    body: str,
    to_email: Optional[str] = None
) -> bool:
    """Send an email notification to a user.

    Args:
        user_id: The user ID to notify (used to lookup email if to_email not provided)
        subject: Email subject line
        body: Email body content
        to_email: Optional explicit email address

    Returns:
        True if email was sent successfully, False otherwise

    Note:
        In production, this would:
        1. Look up user email from database/user service
        2. Use async SMTP library (aiosmtplib)
        3. Support HTML templates
        4. Handle retries and rate limiting
    """
    # TODO: Implement actual email sending
    # For now, just log the notification
    logger.info(
        f"EMAIL NOTIFICATION (mock): "
        f"To: {to_email or f'user:{user_id}'} | "
        f"Subject: {subject} | "
        f"Body: {body[:100]}..."
    )

    # In production, implement with aiosmtplib:
    # import aiosmtplib
    # from email.message import EmailMessage
    #
    # if not to_email:
    #     to_email = await lookup_user_email(user_id)
    #
    # message = EmailMessage()
    # message["From"] = FROM_EMAIL
    # message["To"] = to_email
    # message["Subject"] = subject
    # message.set_content(body)
    #
    # await aiosmtplib.send(
    #     message,
    #     hostname=SMTP_HOST,
    #     port=SMTP_PORT,
    #     username=SMTP_USER,
    #     password=SMTP_PASSWORD,
    #     start_tls=True
    # )

    return True
