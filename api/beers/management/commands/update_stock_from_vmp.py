import requests, json
from beers.models import Beer, ExternalAPI, Store, Stock
from django.utils import timezone
from django.core.management.base import BaseCommand

def call_api(url, storeid, page):
    params = {'query':':name-asc:visibleInSearch:true:mainCategory:øl:availableInStores:'+str(storeid)+':','pageSize':100,'currentPage':page}
    request = requests.get(url = url, params = params)
    response = json.loads(request.text)
    total_pages = response['pagination']['totalPages']

    return(response, total_pages)

class Command(BaseCommand):
    # Updates the database with all beers from vinmonopolet

    def handle(self, *args, **options):
        baseurl = ExternalAPI.objects.get(name="vinmonopolet").baseurl      
        url = baseurl+'products/search/'

        updated = 0
        created = 0

        stores = Store.objects.all()

        for store in stores:
            stocked_beer = []
            response, total_pages = call_api(url, store.storeid, 0)

            # Update all beers in stock
            for page in range(0,total_pages):
                try:
                    response, total_pages = call_api(url, store.storeid, page)

                    for r in response['products']:
                        # Find beer
                        beer = Beer.objects.get(vmp_id=int(r['code']))
                        stocked_beer.append(beer)

                        quantity = int(r['availability']['storeAvailability']['mainText'].split()[1])
                        
                        try:
                            stock = Stock.objects.get(store=store, beer=beer)
                            stock.quantity = quantity
                            stock.save()
                            
                            updated += 1

                        except Stock.DoesNotExist:
                            stock = Stock.objects.create(
                            store = store,
                            beer = beer,
                            quantity = quantity,
                            )

                            created += 1

                except:
                    continue

            # Remove all beers no longer in stock

            Stock.objects.filter(store=store).exclude(beer__in=stocked_beer).delete()

        
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} stocks and created {created} new stocks!'))