"""
Utilities for reading static (and media) files from the configured storage backend.

Works with both local FileSystemStorage and S3-compatible storage (e.g. RustFS / MinIO).
"""

from __future__ import annotations

from django.core.files.storage import storages


def get_staticfiles_storage():
    """Return the configured staticfiles storage backend."""
    return storages["staticfiles"]


def get_default_storage():
    """Return the configured default (media) storage backend."""
    return storages["default"]


def read_static_file(path: str) -> bytes:
    """Read a static file from the configured staticfiles storage."""
    storage = get_staticfiles_storage()
    if not storage.exists(path):
        msg = f"Static file not found: {path}"
        raise FileNotFoundError(msg)
    with storage.open(path, "rb") as f:
        return f.read()


def read_media_file(path: str) -> bytes:
    """Read a file from the configured default (media) storage."""
    storage = get_default_storage()
    if not storage.exists(path):
        msg = f"Media file not found: {path}"
        raise FileNotFoundError(msg)
    with storage.open(path, "rb") as f:
        return f.read()


def static_file_exists(path: str) -> bool:
    """Return True if the static file exists in storage."""
    return get_staticfiles_storage().exists(path)


def media_file_exists(path: str) -> bool:
    """Return True if the media file exists in storage."""
    return get_default_storage().exists(path)
