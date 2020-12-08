import csv, pytz
import pandas as pd
from beers.models import Beer, SiteSetting
from django.utils import timezone
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        vinmonopolet = SiteSetting.objects.get(name='vinmonopolet')
        styles = ['Klosterstil', 'Saison farmhouse ale', 'Barley wine', 'Spesial', 'Hveteøl',
                'Porter & stout', 'Pale ale', 'Mørk lager', 'Brown ale', 'India pale ale', 
                'Lys ale', 'Lys lager', 'Surøl', 'Red/amber', 'Mjød', 'Alkoholfritt øl', 'Scotch ale']

        df = pd.read_csv(vinmonopolet.url, sep=';')
        df = df.loc[df['Varetype'].isin(styles)]
        
        for index, row in df.iterrows():
            try:
                beer = Beer.objects.get(beerid=int(row['Varenummer']))
                beer.name = row['Varenavn']
                beer.brewery = row['Produsent']
                beer.abv = float(row['Alkohol'].replace(',','.'))
                beer.country = row['Land']
                beer.price = float(row['Pris'].replace(',','.'))
                beer.volume = float(row['Volum'].replace(',','.'))
                beer.vinmonopolet_url = row['Vareurl']
                beer.vinmonopolet_updated = timezone.now()
                beer.save()

            except Beer.DoesNotExist:
                beer = Beer.objects.create(
                beerid = int(row['Varenummer']),
                name = row['Varenavn'],
                brewery = row['Produsent'],
                abv = float(row['Alkohol'].replace(',','.')),
                country = row['Land'],
                price = float(row['Pris'].replace(',','.')),
                volume = float(row['Volum'].replace(',','.')),
                vinmonopolet_url = row['Vareurl'],
                vinmonopolet_updated = timezone.now(),
                )

        self.stdout.write(self.style.SUCCESS('Successfully updated database from Vinmonpolet CSV'))