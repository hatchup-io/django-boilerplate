"""Minimal document creation: save file to storage and create Document record."""

import hashlib
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage

from document.models import Document


def create_document(*, user, file_obj, type_id=None) -> Document:
    """Save uploaded file and create Document. Returns the Document instance."""
    original_name = getattr(file_obj, "name", "upload") or "upload"
    ext = Path(original_name).suffix or ""
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = f"documents/{filename}"
    path = default_storage.save(file_path, file_obj)
    size = file_obj.size if hasattr(file_obj, "size") else 0
    content_hash = ""
    if hasattr(file_obj, "read"):
        file_obj.seek(0)
        content_hash = hashlib.sha256(file_obj.read()).hexdigest()
        file_obj.seek(0)
    doc = Document.objects.create(
        user=user,
        type_id=type_id,
        filename=path,
        original_filename=original_name,
        file_type=ext.lstrip(".").lower() or "bin",
        file_path=path,
        file_size_bytes=size,
        content_hash=content_hash,
    )
    return doc
