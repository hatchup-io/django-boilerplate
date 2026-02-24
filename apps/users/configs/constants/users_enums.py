from django.db import models


class UserLegalType(models.TextChoices):
    INDIVIDUAL = "individual", "Individual"
    LEGAL = "legal", "Legal"
