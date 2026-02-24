"""Email delivery service for OTP and other transactional emails."""

import threading

from django.conf import settings
from django.core.mail import send_mail


class EmailService:
    """Service for sending transactional emails."""

    OTP_EXPIRY_MINUTES = 10

    @staticmethod
    def _send_otp_email_sync(email: str, otp_code: str, purpose: str, user_type: str) -> bool:
        """Send OTP email synchronously (called from thread or directly)."""
        subject = "Your verification code"
        if purpose == "login":
            subject = "Your login verification code"
        elif purpose == "register":
            subject = "Your registration verification code"
        message = (
            f"Your verification code is: {otp_code}\n\n"
            f"This code expires in {EmailService.OTP_EXPIRY_MINUTES} minutes."
        )
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
        return True

    @staticmethod
    def send_otp_email(
        email: str,
        otp_code: str,
        purpose: str = "login",
        user_type: str = "client",
        async_send: bool = True,
    ) -> bool:
        """Send OTP via email, optionally in a background thread."""
        if async_send:
            thread = threading.Thread(
                target=EmailService._send_otp_email_sync,
                args=(email, otp_code, purpose, user_type),
                daemon=True,
            )
            thread.start()
            return True
        return EmailService._send_otp_email_sync(email, otp_code, purpose, user_type)
