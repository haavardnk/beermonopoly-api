import requests, json
from itertools import chain
from urllib.parse import quote
from beers.models import Beer, ExternalAPI
from django.utils import timezone
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    # Updates the database with information from Untappd.
    def handle(self, *args, **options):
        untappd = ExternalAPI.objects.get(name='untappd')
        api_client_id = untappd.api_client_id
        api_client_secret = untappd.api_client_secret
        baseurl = untappd.baseurl
        
        api_remaining = '100'
        updated = 0

        #First priority, recheck prioritized wrong matches
        beers1 = Beer.objects.filter(untpd_id__isnull=False, prioritize_recheck=True, active=True)
        #Second priority: never updated rating
        beers2 = Beer.objects.filter(untpd_id__isnull=False, rating__isnull=True, active=True)
        #Second priority, latest updated rating
        beers3 = Beer.objects.filter(untpd_id__isnull=False, active=True).order_by('untpd_updated')

        beers = list(chain(beers1, beers2, beers3))

        for beer in beers:
            if int(api_remaining) <= 5:
                break

            url = baseurl+"beer/info/"+str(beer.untpd_id)+"?client_id="+api_client_id+"&client_secret="+api_client_secret
            request = requests.get(url)
            response = json.loads(request.text)

            try:
                b = response['response']['beer']

                beer.untpd_name = b['beer_name']
                beer.brewery = b['brewery']['brewery_name']
                beer.rating = b['rating_score']
                beer.checkins = b['rating_count']
                beer.style = b['beer_style']
                beer.description = b['beer_description']
                beer.abv = b['beer_abv']
                beer.ibu = b['beer_ibu']
                beer.label_url = b['beer_label_hd']
                beer.untpd_url = "https://untappd.com/b/"+b['beer_slug']+"/"+str(b['bid'])
                beer.untpd_updated = timezone.now()
                if beer.prioritize_recheck == True:
                    beer.verified_match = True
                beer.prioritize_recheck = False
                beer.save()

                api_remaining = request.headers['X-Ratelimit-Remaining']
                updated += 1

            except:
                api_remaining = request.headers['X-Ratelimit-Remaining']
                continue


        self.stdout.write(self.style.SUCCESS(f'Updated {updated} beers. {api_remaining} api calls remaining'))




