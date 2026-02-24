"""OTP generation, storage, verification, and email delivery."""

import logging
import secrets
import string

from django.conf import settings
from django.core.cache import cache

from notification.services.email_service import EmailService

logger = logging.getLogger(__name__)

OTP_PURPOSE_LOGIN = "login"
OTP_PURPOSE_REGISTER = "register"
OTP_LENGTH = 6
OTP_TTL_SECONDS = 600
OTP_VERIFICATION_ID_TTL_SECONDS = 300
OTP_CACHE_KEY_PREFIX = "otp"
OTP_VERIFICATION_CACHE_KEY_PREFIX = "otp_verification"


def _cache_key(email: str, purpose: str) -> str:
    email_clean = email.strip().lower()
    return f"{OTP_CACHE_KEY_PREFIX}:{purpose}:{email_clean}"


def generate_otp(length: int = OTP_LENGTH) -> str:
    """Generate a numeric OTP."""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def store_otp(email: str, otp: str, purpose: str, ttl: int = OTP_TTL_SECONDS) -> None:
    """Store OTP in cache. Requires a shared cache (e.g. Redis) when using multiple processes."""
    key = _cache_key(email, purpose)
    cache.set(key, otp, timeout=ttl)
    stored = cache.get(key)
    if stored is None:
        logger.warning(
            "OTP cache set did not persist (key=%s). "
            "Ensure Redis is running and REDIS_URL is set, or use a single process; "
            "LocMemCache is process-local and will not work with multiple workers.",
            key,
        )


def get_otp(email: str, purpose: str) -> str | None:
    """Retrieve OTP from cache."""
    key = _cache_key(email, purpose)
    return cache.get(key)


def verify_and_consume_otp(email: str, otp: str, purpose: str) -> bool:
    """Verify OTP and delete it from cache (one-time use)."""
    key = _cache_key(email, purpose)
    stored = cache.get(key)
    if stored is None:
        return False
    if str(stored) != str(otp).strip():
        return False
    cache.delete(key)
    return True


def verify_otp_and_issue_verification_id(
    email: str, otp: str, purpose: str, ttl: int = OTP_VERIFICATION_ID_TTL_SECONDS
) -> str | None:
    """Verify OTP, consume it, store a verification id in cache, return the id or None."""
    if not verify_and_consume_otp(email, otp, purpose):
        return None
    verification_id = secrets.token_urlsafe(32)
    key = f"{OTP_VERIFICATION_CACHE_KEY_PREFIX}:{verification_id}"
    payload = {"email": email.strip().lower(), "purpose": purpose}
    cache.set(key, payload, timeout=ttl)
    return verification_id


def consume_verification_id(verification_id: str) -> dict | None:
    """Get and delete verification payload from cache (one-time use). Return None if invalid."""
    if not (verification_id and verification_id.strip()):
        return None
    key = f"{OTP_VERIFICATION_CACHE_KEY_PREFIX}:{verification_id.strip()}"
    payload = cache.get(key)
    if payload is None:
        return None
    cache.delete(key)
    return payload


def send_otp_email(email: str, otp: str, purpose: str, async_send: bool | None = None) -> bool:
    """Send OTP via email. Uses EmailService with async delivery by default."""
    if async_send is None:
        async_send = getattr(settings, "OTP_EMAIL_ASYNC_SEND", True)
    return EmailService.send_otp_email(
        email=email,
        otp_code=otp,
        purpose=purpose,
        user_type="client",
        async_send=async_send,
    )
