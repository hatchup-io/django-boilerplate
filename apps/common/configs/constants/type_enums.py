from django.db import models
from django.utils.translation import gettext_lazy as _


class TypeScopeChoices(models.TextChoices):
    """Target model for a type (document vs form)."""

    DOCUMENT = "document", _("Document")
    FORM = "form", _("Form")
