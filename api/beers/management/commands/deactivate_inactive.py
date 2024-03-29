from beers.models import Beer, Stock
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # Deactivates all beers which has not been updated x days

    def add_arguments(self, parser):
        parser.add_argument("days", type=int)

    def handle(self, *args, **options):
        time_threshold = timezone.now() - timedelta(days=options["days"])
        beers = Beer.objects.filter(vmp_updated__lte=time_threshold, active=True)

        for beer in beers:
            beer.active = False
            beer.save()

        # Delete stock for inactive beers
        stocks = Stock.objects.filter(beer__in=beers)
        stock_count = stocks.count()
        for stock in stocks:
            stock.quantity = 0
            stock.unstocked_at = timezone.now()
            stock.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Set {beers.count()} beers inactive and unstocked {stock_count} beers"
            )
        )
