"""
Email delivery for transactional messages.

The template ships **no task queue**. `send_mail` is called synchronously here.
For production, replace these calls with a queued equivalent (Celery, RQ, dramatiq,
django-q, etc.). Do NOT use `threading.Thread` for fire-and-forget — it dies with
the worker process and has no retries.
"""

from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail

OTP_EXPIRY_MINUTES = 10


def _otp_subject(purpose: str) -> str:
    if purpose == "login":
        return "Your login verification code"
    if purpose == "register":
        return "Your registration verification code"
    return "Your verification code"


def send_otp_email(*, email: str, otp_code: str, purpose: str = "login") -> None:
    """
    Send a one-time-password email synchronously.

    TODO: enqueue with your async backend (Celery, RQ, dramatiq, django-q, ...).
    """
    subject = _otp_subject(purpose)
    message = f"Your verification code is: {otp_code}\n\nThis code expires in {OTP_EXPIRY_MINUTES} minutes."
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[email],
        fail_silently=False,
    )
