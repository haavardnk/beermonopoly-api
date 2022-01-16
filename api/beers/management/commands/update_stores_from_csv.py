import pandas as pd
from beers.models import Store, ExternalAPI
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # Updates stores from CSV file from Vinmonopolet.

    def handle(self, *args, **options):
        url = ExternalAPI.objects.get(name="store_csv").baseurl

        df = pd.read_csv(url, sep=";")

        for index, row in df.iterrows():
            try:
                store = Store.objects.get(store_id=int(row["Butikknummer"]))
                store.name = row["Butikknavn"]
                store.address = row["Gateadresse"]
                store.zipcode = int(row["Gate_postnummer"])
                store.area = row['Post_poststed']
                store.category = row["Kategori"]
                store.gps_lat = row["GPS_breddegrad"]
                store.gps_long = row["GPS_lengdegrad"]
                store.save()

                print("Updated: "+store.name)

            except Store.DoesNotExist:
                store = Store.objects.create(
                    store_id=int(row["Butikknummer"]),
                    name=row["Butikknavn"],
                    address=row["Gateadresse"],
                    zipcode=int(row["Gate_postnummer"]),
                    area = row['Post_poststed'],
                    category=row["Kategori"],
                    gps_lat=row["GPS_breddegrad"],
                    gps_long=row["GPS_lengdegrad"]
                )
                print("Added store: "+store.name)

        self.stdout.write(
            self.style.SUCCESS("Successfully updated stores from Vinmonpolet CSV")
        )
