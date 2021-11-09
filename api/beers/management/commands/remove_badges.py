from beers.models import Badge
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("badge_type", type=str)

    def handle(self, *args, **options):
        badge_type = options["badge_type"]
        Badge.objects.filter(type=badge_type).delete()

        self.stdout.write(
            self.style.SUCCESS(f"All badges of type {badge_type} deleted.")
        )
