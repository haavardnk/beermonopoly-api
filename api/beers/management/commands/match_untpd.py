import requests, json
from urllib.parse import quote
from fuzzywuzzy import process
from beers.models import Beer, ExternalAPI
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        untappd = ExternalAPI.objects.get(name='untappd')
        api_client_id = untappd.api_client_id
        api_client_secret = untappd.api_client_secret
        baseurl = untappd.baseurl
        beers = Beer.objects.filter(untpd_id__isnull=True)

        api_remaining = '100'
        matched_beers = 0

        for beer in beers:
            if int(api_remaining) <= 1:
                break

            try:
                url = baseurl+"search/beer?client_id="+api_client_id+"&client_secret="+api_client_secret+"&q="+quote(beer.vmp_name)+"&limit=5"

                request = requests.get(url)
                response = json.loads(request.text)

                beer2match = beer.vmp_name
                options = []
                for r in response['response']['beers']['items']:
                    options.append(r['brewery']['brewery_name']+" "+r['beer']['beer_name'])
                best_match = process.extractOne(beer2match,options)
                
                match = response['response']['beers']['items'][options.index(best_match[0])]

                beer.untpd_id = match['beer']['bid']
                beer.untpd_url = "https://untappd.com/b/"+match['beer']['beer_slug']+"/"+str(match['beer']['bid'])
                beer.save()

                api_remaining = request.headers['X-Ratelimit-Remaining']
                matched_beers += 1

            except:
                api_remaining = request.headers['X-Ratelimit-Remaining']
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Successfully matched {matched_beers} beers,'+\
                                             f' {api_remaining} remaining API calls.'))
