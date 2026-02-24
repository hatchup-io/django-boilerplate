"""Create base Django Groups: Admin, Super Admin, Client."""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

BASE_ROLE_NAMES = ["Admin", "Super Admin", "Client"]


class Command(BaseCommand):
    help = "Create base roles (Admin, Super Admin, Client) as Django Groups."

    def handle(self, *args, **options):
        for name in BASE_ROLE_NAMES:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group: {name}"))
            else:
                self.stdout.write(f"Group already exists: {name}")
