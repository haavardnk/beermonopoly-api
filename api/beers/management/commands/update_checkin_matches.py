from beers.models import Beer, Checkin
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("limit", type=int)

    def handle(self, *args, **options):
        checkins = Checkin.objects.all().order_by("updated")[: options["limit"]]

        updated = 0

        for checkin in checkins:
            if checkin.untpd_id:
                beers = Beer.objects.filter(untpd_id=checkin.untpd_id)
                if beers:
                    checkin.beer.set(beers)
                    updated += 1
            checkin.save()

        self.stdout.write(self.style.SUCCESS(f"Updated beers on {updated} checkins."))
