"""Override startapp to create new apps under apps/ by default."""

from django.conf import settings
from django.core.management.commands.startapp import Command as StartappCommand


class Command(StartappCommand):
    help = (
        "Creates a Django app directory structure for the given app name in "
        "apps/<app_name>/ (or optionally in the given directory)."
    )

    def handle(self, **options):
        app_name = options.get("name")
        if options.get("directory") is None and app_name:
            options["directory"] = str(settings.BASE_DIR / "apps" / app_name)
        return super().handle(**options)
