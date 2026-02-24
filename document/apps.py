from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DocumentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "document"
    verbose_name = _("Document")
