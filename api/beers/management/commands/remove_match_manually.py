from beers.models import Beer
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        beers = Beer.objects.all()
        for beer in beers:
            beer.match_manually = False
            beer.save()

        self.stdout.write(self.style.SUCCESS("Removed all match manually flags"))
