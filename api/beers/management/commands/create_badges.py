from beers.models import Beer, Badge

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        created = 0

        # Delete all current badges
        Badge.objects.all().delete()

        # Product types
        product_types = list(
            Beer.objects.order_by("main_category")
            .values_list("main_category", flat=True)
            .distinct("main_category")
        )

        for product_type in product_types:
            badge_count = 0

            if product_type == "Øl":
                beer_styles = list(
                    Beer.objects.filter(main_category="Øl")
                    .order_by("sub_category")
                    .values_list("sub_category", flat=True)
                    .distinct("sub_category")
                )

                for style in beer_styles:
                    beers = Beer.objects.filter(
                        main_category=product_type, sub_category=style, active=True
                    ).order_by("-rating")
                    beer_count = beers.count()

                    if beer_count >= 100:
                        badge_count = 10
                    elif beer_count >= 25:
                        badge_count = 5
                    elif beer_count >= 3:
                        badge_count = 3

                    for index, beer in enumerate(beers[:badge_count]):
                        Badge.objects.create(
                            beer=beer, text="#" + str(index + 1) + " " + style
                        )
                        created += 1

            else:
                products = Beer.objects.filter(
                    main_category=product_type, active=True
                ).order_by("-rating")
                product_count = products.count()

                if product_count >= 100:
                    badge_count = 10
                elif product_count >= 25:
                    badge_count = 5
                elif product_count >= 3:
                    badge_count = 3

                for index, product in enumerate(products[:badge_count]):
                    Badge.objects.create(
                        beer=product, text="#" + str(index + 1) + " " + product_type
                    )
                    created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} badges."))
