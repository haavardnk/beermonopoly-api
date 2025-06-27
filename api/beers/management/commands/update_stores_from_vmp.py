import cloudscraper25
import xmltodict
from beers.models import Store, ExternalAPI
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # Updates stores from Vinmonopolet API.
    def handle(self, *args, **options):
        baseurl = ExternalAPI.objects.get(name="vinmonopolet").baseurl
        url = baseurl + "products/search/"

        updated = 0
        created = 0
        failed = 0

        req_url = url + "?currentPage=0&fields=FULL&pageSize=1&query="

        try:
            scraper = cloudscraper25.create_scraper(interpreter="nodejs")
            request = scraper.get(req_url).text
            response = xmltodict.parse(request)

        except Exception as e:
            print(e.with_traceback)

        stores = response["productCategorySearchPage"]["facets"][0]["values"]

        for store in stores:
            try:
                detail_url = baseurl + "stores/" + store["code"]
                detail_request = scraper.get(detail_url).text
                detail_response = response = xmltodict.parse(detail_request)

                store_details = detail_response["pointOfService"]

            except Exception as e:
                failed += 1
                print(e.with_traceback)
                continue

            try:
                s = Store.objects.get(store_id=store["code"])
                s.name = store_details["displayName"]
                s.address = store_details["address"]["line1"]
                s.zipcode = store_details["address"]["postalCode"]
                s.area = store_details["address"]["town"]
                s.category = store_details["assortment"]
                s.gps_lat = store_details["geoPoint"]["latitude"]
                s.gps_long = store_details["geoPoint"]["longitude"]

                s.save()
                updated += 1

            except Store.DoesNotExist:
                s = Store.objects.create(
                    store_id=store["code"],
                    name=store_details["displayName"],
                    address=store_details["address"]["line1"],
                    zipcode=store_details["address"]["postalCode"],
                    area=store_details["address"]["town"],
                    category=store_details["assortment"],
                    gps_lat=store_details["geoPoint"]["latitude"],
                    gps_long=store_details["geoPoint"]["longitude"],
                )

                created += 1

            except Exception as e:
                failed += 1
                print(e.with_traceback)
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated: {updated}, Created: {created}, Failed: {failed}."
            )
        )
