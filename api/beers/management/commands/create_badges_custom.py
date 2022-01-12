from beers.models import Beer, Badge
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--products", type=str)
        parser.add_argument("--badge_text", type=str)
        parser.add_argument("--badge_type", type=str)

    def handle(self, *args, **options):
        created = 0

        products = options["products"].split(",")
        # Create badges
        for product in products:
            try:
                beer = Beer.objects.get(vmp_id=int(product))
            except Beer.DoesNotExist:
                continue

            try:
                Badge.objects.get(beer=beer, text=options["badge_text"])
                continue
            except Badge.DoesNotExist:
                Badge.objects.create(
                    beer=beer,
                    text=options["badge_text"],
                    type=options["badge_type"],
                )
                created += 1

            except:
                continue

        self.stdout.write(self.style.SUCCESS(f"Created {created} badges."))
