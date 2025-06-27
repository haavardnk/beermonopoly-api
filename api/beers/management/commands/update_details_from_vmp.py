import cloudscraper25
import xmltodict
from beers.models import Beer, ExternalAPI
from django.utils import timezone
from django.core.management.base import BaseCommand


def call_api(url, product):
    req_url = url + str(product) + "?fields=FULL"
    scraper = cloudscraper25.create_scraper(interpreter="nodejs")
    request = scraper.get(req_url).text
    response = xmltodict.parse(request)["product"]

    return response


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("calls", type=int)

    def handle(self, *args, **options):
        baseurl = ExternalAPI.objects.get(name="vinmonopolet_v3").baseurl
        url = baseurl + "products/"

        updated = 0
        failed = 0
        n = options["calls"]

        products_without_details = Beer.objects.filter(
            active=True, vmp_details_fetched=None
        )
        products = products_without_details[:n]

        for product in products:
            try:
                response = call_api(url, product.vmp_id)

                if "vintage" in response:
                    product.year = response["vintage"]
                elif "year" in response:
                    product.year = response["year"]
                if "fullness" in response:
                    product.fullness = response["fullness"]
                if "sweetness" in response:
                    product.sweetness = response["sweetness"]
                if "freshness" in response:
                    product.freshness = response["freshness"]
                if "bitterness" in response:
                    product.bitterness = response["bitterness"]
                if "sugar" in response:
                    product.sugar = float(
                        response["sugar"]
                        .replace("<", "")
                        .replace(",", ".")
                        .split(" ")[-1]
                    )
                if "acid" in response:
                    product.acid = float(response["acid"].replace(",", "."))
                if "color" in response:
                    product.color = response["color"]
                if "smell" in response:
                    product.aroma = response["smell"]
                if "taste" in response:
                    product.taste = response["taste"]
                if "matured" in response:
                    product.storable = response["matured"]
                if "raastoff" in response and "name" in response["raastoff"]:
                    product.raw_materials = response["raastoff"]["name"]
                if "isGoodFor" in response:
                    if not isinstance(response["isGoodFor"], list):
                        product.food_pairing = response["isGoodFor"]["name"]
                    else:
                        product.food_pairing = ", ".join(
                            food["name"] for food in response["isGoodFor"]
                        )
                if "allergens" in response:
                    product.allergens = response["allergens"]
                if "method" in response:
                    product.method = response["method"]
                product.vmp_details_fetched = timezone.now()

                product.save()
                updated += 1

            except Exception:
                failed += 1
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} beers and failed to update {failed} beers. {len(products_without_details)} now miss details."
            )
        )
