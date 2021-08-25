import cloudscraper, xmltodict
from beers.models import Beer, ExternalAPI, VmpNotReleased
from django.utils import timezone
from django.core.management.base import BaseCommand


def call_api(url):
    scraper = cloudscraper.create_scraper(interpreter="nodejs")
    request = scraper.get(url).text
    response = xmltodict.parse(request)

    return response


class Command(BaseCommand):
    # Updates all beers from a list of products ID's of unreleased beers.
    # For use before releases.

    def handle(self, *args, **options):
        baseurl = ExternalAPI.objects.get(name="vinmonopolet").baseurl

        updated = 0
        created = 0

        products = VmpNotReleased.objects.all()

        for product in products:
            url = baseurl + "products/" + str(product.id)
            print(url)
            try:
                response = call_api(url)["product"]

                try:
                    beer = Beer.objects.get(vmp_id=int(response["code"]))
                    beer.vmp_name = response["name"]
                    beer.main_category = response["main_category"]["name"]
                    beer.sub_category = response["main_sub_category"]["name"]
                    beer.country = response["main_country"]["name"]
                    beer.price = response["price"]["value"]
                    beer.volume = response["volume"]["value"]
                    beer.product_selection = response["product_selection"]
                    beer.vmp_url = "https://www.vinmonopolet.no" + response["url"]
                    beer.vmp_updated = timezone.now()
                    if beer.active == False:
                        beer.active = True
                    beer.save()

                    updated += 1
                    product.delete()

                except Beer.DoesNotExist:
                    beer = Beer.objects.create(
                        vmp_id=int(response["code"]),
                        vmp_name=response["name"],
                        main_category=response["main_category"]["name"],
                        sub_category=response["main_sub_category"]["name"],
                        country=response["main_country"]["name"],
                        price=response["price"]["value"],
                        volume=response["volume"]["value"],
                        product_selection=response["product_selection"],
                        vmp_url="https://www.vinmonopolet.no" + response["url"],
                        vmp_updated=timezone.now(),
                    )

                    created += 1
                    product.delete()

            except:
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} beers and created {created} new beers!"
            )
        )
