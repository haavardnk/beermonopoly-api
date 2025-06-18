import cloudscraper, xmltodict
from beers.api.utils import parse_bool
from beers.models import Beer, ExternalAPI
from django.utils import timezone
from django.core.management.base import BaseCommand


def call_api(url, page, product):
    if "alkoholfritt" in product:
        query = (
            ":relevance:visibleInSearch:true:mainCategory:alkoholfritt:mainSubCategory:"
            + product
            + ":"
        )
    else:
        query = ":relevance:visibleInSearch:true:mainCategory:" + product + ":"
    req_url = (
        url + "?currentPage=" + str(page) + "&fields=FULL&pageSize=100&query=" + query
    )
    scraper = cloudscraper.create_scraper(interpreter="nodejs")
    request = scraper.get(req_url).text
    response = xmltodict.parse(request)["productCategorySearchPage"]
    total_pages = response["pagination"]["totalPages"]

    return (response, total_pages)


class Command(BaseCommand):
    # Updates the database with all beers from vinmonopolet

    def handle(self, *args, **options):
        baseurl = ExternalAPI.objects.get(name="vinmonopolet").baseurl
        url = baseurl + "products/search/"

        updated = 0
        created = 0

        products = [
            "øl",
            "sider",
            "mjød",
            "alkoholfritt_alkoholfritt_øl",
            "alkoholfritt_alkoholfri_ingefærøl",
            "alkoholfritt_alkoholfri_sider",
        ]

        for product in products:
            response, total_pages = call_api(url, 0, product)

            for page in range(0, int(total_pages)):
                try:
                    response, total_pages = call_api(url, page, product)

                    for b in response["products"]:
                        try:
                            beer = Beer.objects.get(vmp_id=int(b["code"]))
                            beer.vmp_name = b["name"]
                            beer.main_category = b["main_category"]["name"]
                            if b["main_sub_category"]:
                                beer.sub_category = b["main_sub_category"]["name"]
                            beer.country = b["main_country"]["name"]
                            beer.price = b["price"]["value"]
                            beer.volume = float(b["volume"]["value"]) / 100.0
                            beer.price_per_volume = float(b["price"]["value"]) / (
                                float(b["volume"]["value"]) / 100.0
                            )
                            beer.product_selection = b["product_selection"]
                            beer.vmp_url = "https://www.vinmonopolet.no" + b["url"]
                            beer.post_delivery = parse_bool(
                                b["productAvailability"]["deliveryAvailability"][
                                    "availableForPurchase"
                                ]
                            )
                            beer.store_delivery = (
                                b["productAvailability"]["storesAvailability"]["infos"][
                                    "readableValue"
                                ]
                                == "Kan bestilles til alle butikker"
                            )
                            beer.vmp_updated = timezone.now()
                            if beer.active == False:
                                beer.active = True
                            beer.save()

                            updated += 1

                        except Beer.DoesNotExist:
                            beer = Beer.objects.create(
                                vmp_id=int(b["code"]),
                                vmp_name=b["name"],
                                main_category=b["main_category"]["name"],
                                country=b["main_country"]["name"],
                                price=b["price"]["value"],
                                volume=float(b["volume"]["value"]) / 100.0,
                                price_per_volume=float(b["price"]["value"])
                                / (float(b["volume"]["value"]) / 100.0),
                                product_selection=b["product_selection"],
                                post_delivery=parse_bool(
                                    b["productAvailability"]["deliveryAvailability"][
                                        "availableForPurchase"
                                    ]
                                ),
                                store_delivery=b["productAvailability"][
                                    "storesAvailability"
                                ]["infos"]["readableValue"]
                                == "Kan bestilles til alle butikker",
                                vmp_url="https://www.vinmonopolet.no" + b["url"],
                                vmp_updated=timezone.now(),
                            )

                            if b["main_sub_category"]:
                                beer.sub_category = b["main_sub_category"]["name"]
                                beer.save()

                            created += 1

                except:
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} beers and created {created} new beers!"
            )
        )
