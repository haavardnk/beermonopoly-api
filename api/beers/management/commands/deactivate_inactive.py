from beers.models import Beer
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    # Deactivates all beers which has not been updated for a month
    def handle(self, *args, **options):
        time_threshold = timezone.now() - timedelta(days=30)
        beers = Beer.objects.filter(vmp_updated__lte=time_threshold)

        for beer in beers:
            beer.active = False
            beer.save()