import cloudscraper, xmltodict
from django.utils import timezone
from beers.models import Beer, ExternalAPI, Store, Stock
import re
from django.core.management.base import BaseCommand


def call_api(url, store_id, page, product):
    if "alkoholfritt" in product:
        query = (
            ":name-asc:visibleInSearch:true:mainCategory:alkoholfritt:mainSubCategory:"
            + product
            + ":availableInStores:"
            + str(store_id)
            + ":"
        )
    else:
        query = (
            ":name-asc:visibleInSearch:true:mainCategory:"
            + product
            + ":availableInStores:"
            + str(store_id)
            + ":"
        )
    req_url = (
        url + "?currentPage=" + str(page) + "&fields=FULL&pageSize=100&query=" + query
    )
    scraper = cloudscraper.CloudScraper()
    request = scraper.get(req_url).text

    response = xmltodict.parse(request)

    response = response["productCategorySearchPage"]
    total_pages = response["pagination"]["totalPages"]

    return (response, total_pages)


class Command(BaseCommand):
    # Updates the database with all beers from vinmonopolet

    def add_arguments(self, parser):
        parser.add_argument("stores", type=int)

    def handle(self, *args, **options):
        baseurl = ExternalAPI.objects.get(name="vinmonopolet").baseurl
        url = baseurl + "products/search/"

        updated = 0
        stocked = 0
        unstocked = 0
        stores_updated = 0
        n = options["stores"]
        stores = Store.objects.all().order_by("store_stock_updated")[:n]
        products = [
            "øl",
            "sider",
            "mjød",
            "alkoholfritt_alkoholfritt_øl",
            "alkoholfritt_alkoholfri_ingefærøl",
            "alkoholfritt_alkoholfri_sider",
        ]

        for store in stores.iterator():
            stocked_beer = []

            for product in products:
                try:
                    response, total_pages = call_api(url, store.store_id, 0, product)
                except Exception as e:
                    raise (e)

                # Update all beers in stock
                for page in range(0, int(total_pages)):
                    try:
                        response, total_pages = call_api(
                            url, store.store_id, page, product
                        )

                        for res in response["products"]:
                            # Find beer
                            beer = Beer.objects.get(vmp_id=int(res["code"]))
                            stocked_beer.append(beer)

                            quantity = [
                                int(s)
                                for s in re.findall(
                                    r"\b\d+\b",
                                    res["availability"]["storeAvailability"][
                                        "mainText"
                                    ],
                                )
                            ][0]

                            try:
                                stock = Stock.objects.get(store=store, beer=beer)
                                if stock.quantity == 0 and quantity != 0:
                                    stock.stocked_at = timezone.now()
                                stock.quantity = quantity
                                stock.save()

                                updated += 1

                            except Stock.DoesNotExist:
                                stock = Stock.objects.create(
                                    store=store,
                                    beer=beer,
                                    quantity=quantity,
                                    stocked_at=timezone.now(),
                                )

                                stocked += 1

                    except:
                        continue

            # Remove all beers no longer in stock in the store
            if len(stocked_beer) != 0:
                stocks = (
                    Stock.objects.filter(store=store)
                    .exclude(beer__in=stocked_beer)
                    .exclude(quantity=0)
                )
                unstocked += stocks.count()
                for stock in stocks:
                    stock.quantity = 0
                    stock.unstocked_at = timezone.now()
                    stock.save()

            store.store_stock_updated = timezone.now()
            store.save()

            stores_updated += 1

            print(
                f"Updated stock: {updated} Stocked: {stocked} Out of stock: {unstocked} Stores updated: {stores_updated}/{len(stores)}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated stock: {updated} Stocked: {stocked} Out of stock: {unstocked} Stores updated: {stores_updated}/{len(stores)}"
            )
        )
