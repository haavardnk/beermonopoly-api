import csv
import pandas as pd
from beers.models import Store, ExternalAPI
from django.utils import timezone
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    # Updates stores from CSV file from Vinmonopolet.

    def handle(self, *args, **options):
        url = ExternalAPI.objects.get(name="store_csv").baseurl

        df = pd.read_csv(url, sep=';')
        
        for index, row in df.iterrows():
            try:
                store = Store.objects.get(store_id=int(row['Butikknummer']))
                store.name = row['Butikknavn']
                store.address = row['Gateadresse']
                store.zipcode = int(row['Gate_postnummer'])
                store.category = row['Kategori']
                store.gps_lat = float(row['GPS_breddegrad'])
                store.gps_long = float(row['GPS_lengdegrad'])
                store.save()

            except Store.DoesNotExist:
                store = Store.objects.create(
                store_id = int(row['Butikknummer']),
                name = row['Butikknavn'],
                address = row['Gateadresse'],
                zipcode = int(row['Gate_postnummer']),
                category = row['Kategori'],
                gps_lat = float(row['GPS_breddegrad']),
                gps_long = float(row['GPS_lengdegrad']),
                )

        self.stdout.write(self.style.SUCCESS('Successfully updated stores from Vinmonpolet CSV'))