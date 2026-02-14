"""
Example background tasks.
"""

import logging

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.send_email")
def send_email_task(email: str, subject: str, body: str) -> dict[str, str]:
    """
    Example task to send email.

    Args:
        email: Recipient email
        subject: Email subject
        body: Email body

    Returns:
        Task result
    """
    logger.info(f"Sending email to {email}")

    # Simulate email sending
    # In production, integrate with SendGrid, AWS SES, etc.

    logger.info(f"Email sent successfully to {email}")

    return {
        "status": "success",
        "email": email,
        "subject": subject,
    }
