from beers.models import Beer, Badge
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        created = 0

        # Delete all current badges
        Badge.objects.filter(type="Top Style").delete()

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
                    Beer.objects.order_by("style")
                    .values_list("style", flat=True)
                    .distinct("style")
                )

                for style in beer_styles:
                    beers = Beer.objects.filter(
                        main_category=product_type, sub_category=style, active=True
                    ).order_by("-rating")
                    beer_count = beers.count()

                    if beer_count >= 300:
                        badge_count = 25
                    elif beer_count >= 100:
                        badge_count = 15
                    elif beer_count >= 50:
                        badge_count = 10
                    elif beer_count >= 25:
                        badge_count = 5
                    elif beer_count >= 10:
                        badge_count = 3

                    for index, beer in enumerate(beers[:badge_count]):
                        Badge.objects.create(
                            beer=beer,
                            text="#" + str(index + 1) + " " + style,
                            type="Top Style",
                        )
                        created += 1

            else:
                products = Beer.objects.filter(
                    main_category=product_type, active=True
                ).order_by("-rating")
                product_count = products.count()

                if product_count >= 300:
                    badge_count = 25
                elif product_count >= 15:
                    badge_count = 15
                elif product_count >= 50:
                    badge_count = 10
                elif product_count >= 25:
                    badge_count = 5
                elif product_count >= 10:
                    badge_count = 3

                for index, product in enumerate(products[:badge_count]):
                    Badge.objects.create(
                        beer=product,
                        text="#" + str(index + 1) + " " + product_type,
                        type="Top Style",
                    )
                    created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} badges."))
