import re
import time
from googlesearch import search
from fuzzywuzzy import process, fuzz
from beers.models import Beer
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("calls", type=int)

    # Matches beers from beername to untappd ID.
    def handle(self, *args, **options):
        beers = Beer.objects.filter(
            untpd_id__isnull=True, match_manually=False, active=True
        )
        matched = 0
        failed = 0
        failed_beers = []

        for beer in beers[: options["calls"]]:
            time.sleep(1)
            # Use fuzzywuzzy to assert matches instead of just taking top result
            beer2match = beer.vmp_name
            options = []
            indexes = {}

            results = list(
                search(
                    beer2match + " site:https://untappd.com/b/", 4, "no", advanced=True
                )
            )
            for result in results:
                options.append(result.title)
                indexes[result.title] = result.url

            best_match = process.extractOne(beer2match, options, scorer=fuzz.ratio)
            # Only match if match is over 40 (Levenshtein distance)

            # Updates database
            try:
                if (
                    best_match[1] > 40
                    and "https://untappd.com/b/" in indexes[best_match[0]]
                ):
                    beer.untpd_id = int(
                        re.sub(r"\D+$", "", indexes[best_match[0]]).split("/")[-1]
                    )
                    beer.untpd_url = re.sub(r"\D+$", "", indexes[best_match[0]])
                    beer.save()
                    matched += 1
                    print(f"Matched {beer} as {best_match[0]}")

                    continue

                else:
                    beer.description = "Missing on Untappd."
                    beer.match_manually = True
                    beer.save()
                    failed += 1
                    failed_beers.append(beer)
                    print(f"Failed to match {beer}... Possible option: {best_match[0]}")
                    continue

            except:
                beer.description = "Missing on Untappd."
                beer.match_manually = True
                beer.save()
                failed += 1
                failed_beers.append(beer)
                print(f"Failed to match {beer}...")
                continue

        print(f"Matched: {matched} Failed: {failed}")

        self.stdout.write(self.style.SUCCESS(f"Matched: {matched} Failed: {failed}"))
