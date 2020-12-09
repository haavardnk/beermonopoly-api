import requests, json
from beers.models import Beer, ExternalAPI
from django.utils import timezone
from django.core.management.base import BaseCommand

def call_api(url, page, category):
    params = {'query':':relevance:visibleInSearch:true:mainCategory:'+category+':','pageSize':100,'currentPage':page}
    request = requests.get(url = url, params = params)
    response = json.loads(request.text)
    total_pages = response['pagination']['totalPages']

    return(response, total_pages)

class Command(BaseCommand):

    def handle(self, *args, **options):
        # Get info from all beers
        baseurl = ExternalAPI.objects.get(name="vinmonopolet").baseurl      
        url = baseurl+'products/search/'

        categories = ['øl', 'mjød']
        
        for cat in categories:
            response, total_pages = call_api(url, 0, cat)
            for page in range(0,total_pages):
                try:
                    response, total_pages = call_api(url, page, cat)

                    for b in response['products']:
                        try:
                            beer = Beer.objects.get(beerid=int(b['code']))
                            beer.name = b['name']
                            beer.category = b['main_sub_category']['name']
                            beer.country = b['main_country']['name']
                            beer.price = b['price']['value']
                            beer.volume = b['volume']['value']
                            beer.product_selection = b['product_selection']
                            beer.vinmonopolet_url = "https://www.vinmonopolet.no"+b['url']
                            beer.vinmonopolet_updated = timezone.now()
                            beer.save()

                        except Beer.DoesNotExist:
                            beer = Beer.objects.create(
                            beerid = int(b['code']),
                            name = b['name'],
                            category = b['main_sub_category']['name'],
                            country = b['main_country']['name'],
                            price = b['price']['value'],
                            volume = b['volume']['value'],
                            product_selection = b['product_selection'],
                            vinmonopolet_url = "https://www.vinmonopolet.no/"+b['url'],
                            vinmonopolet_updated = timezone.now()
                            )

                except:
                    continue

        


        #Fill details