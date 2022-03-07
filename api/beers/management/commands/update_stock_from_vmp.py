import cloudscraper, xmltodict
from django.utils import timezone
from beers.models import Beer, ExternalAPI, Store, Stock
from django.core.management.base import BaseCommand


def call_api(url, store_id, page, product):
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
        created = 0
        deleted = 0
        stores_updated = 0
        n = options["stores"]
        stores = Store.objects.all().order_by("store_stock_updated")[:n]
        products = ["øl", "sider", "mjød"]

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

                        for r in response["products"]:
                            # Find beer
                            beer = Beer.objects.get(vmp_id=int(r["code"]))
                            stocked_beer.append(beer)

                            quantity = int(
                                r["availability"]["storeAvailability"][
                                    "mainText"
                                ].split()[1]
                            )

                            try:
                                stock = Stock.objects.get(store=store, beer=beer)
                                stock.quantity = quantity
                                stock.save()

                                updated += 1

                            except Stock.DoesNotExist:
                                stock = Stock.objects.create(
                                    store=store,
                                    beer=beer,
                                    quantity=quantity,
                                )

                                created += 1

                    except:
                        continue

            # Remove all beers no longer in stock in the store
            if len(stocked_beer) != 0:
                stocks = Stock.objects.filter(store=store).exclude(
                    beer__in=stocked_beer
                )
                deleted += stocks.count()
                stocks.delete()

            store.store_stock_updated = timezone.now()
            store.save()

            stores_updated += 1

            print(
                f"Updated: {updated} Created: {created} Deleted: {deleted} Stores updated: {stores_updated}/{len(stores)}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated: {updated} Created: {created} Deleted: {deleted} Stores updated: {stores_updated}/{len(stores)}"
            )
        )
