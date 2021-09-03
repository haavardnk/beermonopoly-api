import requests, json
from urllib.parse import quote
from fuzzywuzzy import process, fuzz
from beers.models import Beer, ExternalAPI, MatchFilter
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # Matches beers from beername to untappd ID.

    def handle(self, *args, **options):
        untappd = ExternalAPI.objects.get(name="untappd")
        api_client_id = untappd.api_client_id
        api_client_secret = untappd.api_client_secret
        baseurl = untappd.baseurl

        beers = Beer.objects.filter(
            untpd_id__isnull=True, match_manually=False, active=True
        )

        filters = []
        for f in MatchFilter.objects.all():
            filters.append(f.name)
        filters.sort(key=len, reverse=True)

        api_remaining = "100"
        matched = 0
        failed = 0
        failed_beers = []

        for beer in beers:
            # Make query string
            querystring = beer.vmp_name

            # Run three times
            for i in range(1, 4):

                # Remove collab brewery
                if " x " in querystring:
                    querywords = querystring.split()
                    index = querywords.index("x")
                    querystring = " ".join(querywords[:index] + querywords[index + 2 :])

                # Remove filter words (only if the word is more than two words long)
                if len(querystring.split()) > 2:
                    for filter_word in filters:
                        if filter_word in querystring.lower():
                            querywords = querystring.split()
                            resultwords = [
                                word
                                for word in querywords
                                if word.lower() not in filter_word.split()
                            ]
                            querystring = " ".join(resultwords)

            query = querystring

            url = (
                baseurl
                + "search/beer?client_id="
                + api_client_id
                + "&client_secret="
                + api_client_secret
                + "&q="
                + quote(query)
                + "&limit=5"
            )

            try:
                headers = {"User-Agent": "django:Beermonopoly"}
                request = requests.get(url, headers=headers)
                response = json.loads(request.text)
                api_remaining = request.headers["X-Ratelimit-Remaining"]
            except:
                break

            try:
                # Use fuzzywuzzy to assert matches instead of just taking top result
                beer2match = query
                options = []

                for r in response["response"]["beers"]["items"]:
                    # Create options by appending first word in brewery name + beer name
                    options.append(
                        r["brewery"]["brewery_name"].split()[0]
                        + " "
                        + r["beer"]["beer_name"]
                    )
                best_match = process.extractOne(beer2match, options, scorer=fuzz.ratio)

                # Only match if match is over 60 (Levenshtein distance)
                if best_match[1] > 60:
                    # Gets matched beer
                    match = response["response"]["beers"]["items"][
                        options.index(best_match[0])
                    ]

                    # Updates database
                    beer.untpd_id = match["beer"]["bid"]
                    beer.untpd_url = (
                        "https://untappd.com/b/"
                        + match["beer"]["beer_slug"]
                        + "/"
                        + str(match["beer"]["bid"])
                    )
                    beer.save()
                    matched += 1

                else:
                    beer.match_manually = True
                    beer.save()
                    failed += 1
                    failed_beers.append(beer)

            except:
                beer.match_manually = True
                beer.save()
                failed += 1
                failed_beers.append(beer)

            print(f"Matched: {matched} Failed: {failed} API remaining: {api_remaining}")

            # Stop if no api calls remaining
            if int(api_remaining) <= 5:
                break

        self.stdout.write(
            self.style.SUCCESS(
                f"Matched: {matched} Failed: {failed} API remaining: {api_remaining}"
            )
        )
