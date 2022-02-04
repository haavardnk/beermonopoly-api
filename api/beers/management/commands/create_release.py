from beers.models import Beer, Release
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--name", type=str)
        parser.add_argument("--products", type=str)

    def handle(self, *args, **options):
        name = options["name"]
        products = options["products"].split(",")

        beers = 0

        # Create release
        try:
            release = Release.objects.get(name=name)
        except Release.DoesNotExist:
            release = Release.objects.create(name=name)

        # Add beers
        for product in products:
            try:
                beer = Beer.objects.get(vmp_id=int(product))
            except Beer.DoesNotExist:
                continue

            release.beer.add(beer.vmp_id)
            release.save()
            beers += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created release with name: {name} and added {beers} beers."
            )
        )
