from beers.models import Beer, Badge
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        created = 0

        # Delete all current badges
        Badge.objects.filter(type="Top Style").delete()

        # Product types
        styles = []
        all_styles = list(
            filter(
                None,
                list(
                    Beer.objects.order_by("style")
                    .values_list("style", flat=True)
                    .distinct("style")
                    .exclude(style__in=["Other", "Gluten-Free"])
                ),
            )
        )

        for style in all_styles:
            styles.append(style.split("-")[0])
        styles = list(dict.fromkeys(styles))
        styles.append("Gluten-Free")

        # Create badges
        for style in styles:
            badge_count = 0
            products = Beer.objects.filter(
                style__startswith=style, active=True
            ).order_by("-rating")

            if products.count() >= 300:
                badge_count = 25
            elif products.count() >= 100:
                badge_count = 15
            elif products.count() >= 50:
                badge_count = 10
            elif products.count() >= 25:
                badge_count = 5
            elif products.count() >= 10:
                badge_count = 3

            for index, product in enumerate(products[:badge_count]):
                Badge.objects.create(
                    beer=product,
                    text="#" + str(index + 1) + " " + style,
                    type="Top Style",
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} badges."))
