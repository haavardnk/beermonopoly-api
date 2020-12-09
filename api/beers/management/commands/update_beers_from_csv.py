import csv, pytz
import pandas as pd
from beers.models import Beer
from django.utils import timezone
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        url = "https://www.vinmonopolet.no/medias/sys_master/products/products/hbc/hb0/8834253127710/produkter.csv"
        styles = ['Klosterstil', 'Saison farmhouse ale', 'Barley wine', 'Spesial', 'Hveteøl',
                'Porter & stout', 'Pale ale', 'Mørk lager', 'Brown ale', 'India pale ale', 
                'Lys ale', 'Lys lager', 'Surøl', 'Red/amber', 'Mjød', 'Scotch ale']

        df = pd.read_csv(url, sep=';')
        df = df.loc[df['Varetype'].isin(styles)]
        
        for index, row in df.iterrows():
            try:
                beer = Beer.objects.get(vmp_id=int(row['Varenummer']))
                beer.vmp_name = row['Varenavn']
                beer.sub_category = row['Varetype']
                beer.country = row['Land']
                beer.price = float(row['Pris'].replace(',','.'))
                beer.volume = float(row['Volum'].replace(',','.'))
                beer.product_selection = row['Produktutvalg']
                beer.vmp_url = row['Vareurl']
                beer.vmp_updated = timezone.now()
                beer.save()

            except Beer.DoesNotExist:
                beer = Beer.objects.create(
                vmp_id = int(row['Varenummer']),
                vmp_name = row['Varenavn'],
                sub_category = row['Varetype'],
                country = row['Land'],
                price = float(row['Pris'].replace(',','.')),
                volume = float(row['Volum'].replace(',','.')),
                product_selection = row['Produktutvalg'],
                vmp_url = row['Vareurl'],
                vmp_updated = timezone.now(),
                )

        self.stdout.write(self.style.SUCCESS('Successfully updated beers from Vinmonpolet CSV'))