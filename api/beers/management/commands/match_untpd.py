import requests, json
from urllib.parse import quote
from fuzzywuzzy import process, fuzz
from beers.models import Beer, ExternalAPI, MatchFilter
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    # Matches beers from beername to untappd ID.

    def handle(self, *args, **options):
        untappd = ExternalAPI.objects.get(name='untappd')
        api_client_id = untappd.api_client_id
        api_client_secret = untappd.api_client_secret
        baseurl = untappd.baseurl
        beers = Beer.objects.filter(untpd_id__isnull=True, match_manually=False, active=True)
        filters = []
        for f in MatchFilter.objects.all():
            filters.append(f.name)
        filters.sort(key=len, reverse=True)
        brewery_list = []

        api_remaining = '100'
        matched_beers = 0

        for beer in beers:
            # Stop if no api calls remaining
            if int(api_remaining) <= 5:
                break

            # Make query string
            querystring = beer.vmp_name

            # Remove collab brewery
            if ' x ' in querystring:
                querywords = querystring.split()
                index = querywords.index('x')
                querystring = ' '.join(querywords[:index]+querywords[index+2 :]) 

            # Remove filter words (only if the word is long)
            if len(querystring.split()) > 3:
                for filter_word in filters:
                    if filter_word in querystring.lower():
                        querywords = querystring.split()
                        resultwords  = [word for word in querywords if word.lower() not in filter_word.split()]
                        querystring = ' '.join(resultwords)     
            query = querystring 

            url = baseurl+"search/beer?client_id="+api_client_id+"&client_secret="+api_client_secret+"&q="+quote(query)+"&limit=5"
            self.stdout.write(url)

            try:
                request = requests.get(url)
                response = json.loads(request.text)
                api_remaining = request.headers['X-Ratelimit-Remaining']
            except:
                break

            try:
                # Use fuzzywuzzy to assert matches instead of just taking top result
                beer2match = query
                options = []
                
                for r in response['response']['beers']['items']:
                    options.append(r['brewery']['brewery_name']+" "+r['beer']['beer_name'])
                best_match = process.extractOne(beer2match,options,scorer=fuzz.ratio)

                # Only match if match is over 50
                if best_match[1] > 50:
                    # Gets matched beer
                    match = response['response']['beers']['items'][options.index(best_match[0])]

                    # Updates database
                    print("https://untappd.com/b/"+match['beer']['beer_slug']+"/"+str(match['beer']['bid']))
                    beer.untpd_id = match['beer']['bid']
                    beer.untpd_url = "https://untappd.com/b/"+match['beer']['beer_slug']+"/"+str(match['beer']['bid'])
                    beer.save()
                else:
                    beer.match_manually = True
                    beer.save()

                matched_beers += 1

            except:
                beer.match_manually = True
                beer.save()
                continue

        self.stdout.write(self.style.SUCCESS(f'Successfully matched {matched_beers} beers,'+\
                                             f' {api_remaining} remaining API calls.'))


