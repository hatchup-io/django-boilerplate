from __future__ import annotations

import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import sentry_sdk
from django.conf import settings
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django_redis import get_redis_connection
from redis import Redis

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = float(os.getenv("HEALTHCHECK_TIMEOUT_SECONDS", "2.0"))
# CELERY_TIMEOUT = float(os.getenv("HEALTHCHECK_CELERY_TIMEOUT_SECONDS", DEFAULT_TIMEOUT))


def _env_flag(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def _capture_exception(
    message: str, exc: BaseException, *, extra: Optional[Dict[str, Any]] = None
) -> None:
    logger.warning("%s: %s", message, exc, extra=extra)
    sentry_sdk.capture_exception(exc)


@dataclass
class ServiceCheckResult:
    name: str
    status: str
    message: str
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        # Keep payload compact by pruning None values.
        return {key: value for key, value in payload.items() if value is not None}


def _resolve_status(required: bool, degraded_status: str = "degraded") -> str:
    return "unhealthy" if required else degraded_status


def check_redis() -> ServiceCheckResult:
    redis_url = os.getenv("REDIS_URL")
    required = _env_flag("REDIS_REQUIRED", bool(redis_url))
    if not redis_url:
        return ServiceCheckResult(
            name="redis",
            status="skipped",
            message="REDIS_URL not configured; skipping Redis connectivity check.",
        )

    try:
        start_time = time.monotonic()
        connection: Redis = get_redis_connection("default")
        # ``ping`` raises ``RedisError`` on failure, which we capture below.
        connection.ping()
        latency_ms = (time.monotonic() - start_time) * 1000
        return ServiceCheckResult(
            name="redis",
            status="healthy",
            message="Redis ping successful.",
            latency_ms=round(latency_ms, 2),
        )
    except Exception as exc:  # pragma: no cover - dependent on external service
        _capture_exception("Redis connectivity check failed", exc)
        status = _resolve_status(required)
        return ServiceCheckResult(
            name="redis",
            status=status,
            message=f"Redis check failed: {exc}",
        )


def check_cache() -> ServiceCheckResult:
    cache_alias = os.getenv("HEALTHCHECK_CACHE_ALIAS", "default")
    required = _env_flag("CACHE_REQUIRED", False)
    cache_key = f"healthcheck:{os.getpid()}:{int(time.time() * 1000)}"
    try:
        cache = caches[cache_alias]
    except InvalidCacheBackendError as exc:
        _capture_exception(f"Cache alias '{cache_alias}' unavailable", exc)
        status = _resolve_status(required)
        return ServiceCheckResult(
            name="cache",
            status=status,
            message=f"Cache alias '{cache_alias}' is not configured.",
        )

    try:
        start_time = time.monotonic()
        cache.set(cache_key, "ok", timeout=5)
        value = cache.get(cache_key)
        cache.delete(cache_key)
        latency_ms = (time.monotonic() - start_time) * 1000
        if value == "ok":
            return ServiceCheckResult(
                name="cache",
                status="healthy",
                message=f"Cache '{cache_alias}' responded successfully.",
                latency_ms=round(latency_ms, 2),
            )
        status = _resolve_status(required)
        return ServiceCheckResult(
            name="cache",
            status=status,
            message=f"Cache '{cache_alias}' returned unexpected payload.",
        )
    except Exception as exc:  # pragma: no cover - dependent on external service
        _capture_exception(f"Cache '{cache_alias}' check failed", exc)
        status = _resolve_status(required)
        return ServiceCheckResult(
            name="cache",
            status=status,
            message=f"Cache check failed: {exc}",
        )


def gather_service_statuses() -> Dict[str, Dict[str, Any]]:
    checks = [
        # check_redis(),
        # check_cache(),
    ]
    return {check.name: check.to_dict() for check in checks}


def derive_overall_status(service_results: Dict[str, Dict[str, Any]]) -> str:
    priority = {
        "healthy": 0,
        "skipped": 1,
        "disabled": 1,
        "degraded": 2,
        "unhealthy": 3,
    }
    highest = 0
    for result in service_results.values():
        service_status = result.get("status", "healthy")
        highest = max(highest, priority.get(service_status, 3))
    if highest >= 3:
        return "unhealthy"
    if highest == 2:
        return "degraded"
    return "healthy"


def basic_health_payload() -> Dict[str, Any]:
    return {
        "status": "ok",
        "environment": getattr(settings, "ENVIRONMENT", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def ready_health_payload() -> Tuple[Dict[str, Any], int]:
    results = gather_service_statuses()
    overall_status = derive_overall_status(results)
    status_code = 503 if overall_status == "unhealthy" else 200
    payload = {
        "status": overall_status,
        "environment": getattr(settings, "ENVIRONMENT", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": results,
    }
    return payload, status_code
