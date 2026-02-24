from django.db import models


class NotificationCategoryChoices(models.TextChoices):
    ALERT = "alert", "Alert"
    INFO = "info", "Info"
    SUCCESS = "success", "Success"
    WARNING = "warning", "Warning"
    ERROR = "error", "Error"


class NotificationAudienceChoices(models.TextChoices):
    ALL = "all", "All users"
    STARTUP = "startup", "Startup"
    INVESTOR = "investor", "Investor"
