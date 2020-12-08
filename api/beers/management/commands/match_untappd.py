import requests, json
from urllib.parse import quote
from beers.models import Beer, SiteSetting
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        untappd = SiteSetting.objects.get(name='untappd')
        api_client_id = untappd.api_client_id
        api_client_secret = untappd.api_client_secret
        beers = Beer.objects.filter(untappd_id__isnull=True)

        api_remaining = '1'
        matched_beers = 0

        for beer in beers:
            if int(api_remaining) <= 1:
                break

            try:
                query = quote(beer.name)
                url = "https://api.untappd.com/v4/search/beer?client_id="+\
                        api_client_id+"&client_secret="+api_client_secret+"&q="+query

                request = requests.get(url)
                response = json.loads(request.text)
                match = response['response']['beers']['items'][0]

                beer.untappd_id = match['beer']['bid']
                beer.save()

                api_remaining = request.headers['X-Ratelimit-Remaining']
                matched_beers += 1

            except:
                api_remaining = request.headers['X-Ratelimit-Remaining']
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Successfully matched {matched_beers} beers,'+\
                                             f' {api_remaining} remaining API calls.'))
