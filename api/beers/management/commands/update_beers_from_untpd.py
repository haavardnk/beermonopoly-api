import requests, json
from json.decoder import JSONDecodeError
from itertools import chain
from beers.models import Beer, ExternalAPI
from django.utils import timezone
from datetime import timedelta
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    # Updates the database with information from Untappd.
    def handle(self, *args, **options):
        untappd = ExternalAPI.objects.get(name="untappd")
        api_client_id = untappd.api_client_id
        api_client_secret = untappd.api_client_secret
        baseurl = untappd.baseurl

        api_remaining = "100"
        updated = 0

        # First priority, recheck prioritized corrected matches
        beers1 = Beer.objects.filter(
            untpd_id__isnull=False, prioritize_recheck=True, active=True
        )
        # Second priority: never updated rating
        beers2 = Beer.objects.filter(
            untpd_id__isnull=False, rating__isnull=True, active=True
        )
        # Third priority: under 500 checkins, but not more often than every 7 day
        time_threshold = timezone.now() - timedelta(days=7)
        beers3 = Beer.objects.filter(
            untpd_updated__lte=time_threshold,
            untpd_id__isnull=False,
            active=True,
            checkins__lte=500,
        )
        # Fourth priority, latest updated rating
        beers4 = Beer.objects.filter(untpd_id__isnull=False, active=True).order_by(
            "untpd_updated"
        )

        # Create list of unique beers (Same beers can appear in different priorities.)
        beers = []
        for x in list(chain(beers1, beers2, beers3, beers4)):
            if x not in beers:
                beers.append(x)

        for beer in beers:
            if int(api_remaining) <= 5:
                break

            try:
                url = (
                    baseurl
                    + "beer/info/"
                    + str(beer.untpd_id)
                    + "?client_id="
                    + api_client_id
                    + "&client_secret="
                    + api_client_secret
                )
                headers = {"User-Agent": "django:Beermonopoly"}
                request = requests.get(url, headers=headers)
                response = json.loads(request.text)

            except JSONDecodeError:
                continue

            except Exception as e:
                print(e)
                break

            try:
                b = response["response"]["beer"]
                beer.untpd_name = b["beer_name"]
                beer.brewery = b["brewery"]["brewery_name"]
                beer.rating = b["rating_score"]
                beer.checkins = b["rating_count"]
                beer.style = b["beer_style"]
                beer.description = b["beer_description"]
                beer.abv = b["beer_abv"]
                beer.ibu = b["beer_ibu"]
                beer.label_url = b["beer_label_hd"]
                beer.untpd_url = (
                    "https://untappd.com/b/" + b["beer_slug"] + "/" + str(b["bid"])
                )
                beer.untpd_updated = timezone.now()
                beer.prioritize_recheck = False
                beer.save()

                api_remaining = request.headers["X-Ratelimit-Remaining"]
                updated += 1

            except:
                api_remaining = request.headers["X-Ratelimit-Remaining"]
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} beers. {api_remaining} api calls remaining"
            )
        )
