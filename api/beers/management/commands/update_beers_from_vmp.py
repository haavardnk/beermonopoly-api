import requests, json
from beers.models import Beer, ExternalAPI
from django.utils import timezone
from django.core.management.base import BaseCommand

def call_api(url, page):
    params = {'query':':relevance:visibleInSearch:true:mainCategory:øl:','pageSize':100,'currentPage':page}
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
        
        response, total_pages = call_api(url, 0)
        for page in range(0,total_pages):
            try:
                response, total_pages = call_api(url, page)

                for b in response['products']:
                    try:
                        beer = Beer.objects.get(vmp_id=int(b['code']))
                        beer.vmp_name = b['name']
                        beer.main_category = b['main_category']['name']
                        beer.sub_category = b['main_sub_category']['name']
                        beer.country = b['main_country']['name']
                        beer.price = b['price']['value']
                        beer.volume = b['volume']['value']
                        beer.product_selection = b['product_selection']
                        beer.vmp_url = "https://www.vinmonopolet.no"+b['url']
                        beer.vmp_updated = timezone.now()
                        beer.save()
                        
                        updated += 1

                    except Beer.DoesNotExist:
                        beer = Beer.objects.create(
                        vmp_id = int(b['code']),
                        vmp_name = b['name'],
                        main_category = b['main_category']['name'],
                        sub_category = b['main_sub_category']['name'],
                        country = b['main_country']['name'],
                        price = b['price']['value'],
                        volume = b['volume']['value'],
                        product_selection = b['product_selection'],
                        vmp_url = "https://www.vinmonopolet.no"+b['url'],
                        vmp_updated = timezone.now()
                        )

                        created += 1

            except:
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} beers and created {created} new beers!'))