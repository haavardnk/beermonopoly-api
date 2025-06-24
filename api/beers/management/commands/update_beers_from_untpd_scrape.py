import re
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from itertools import chain
from beers.models import Beer
from django.utils import timezone
from datetime import timedelta
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("calls", type=int)

    # Updates the database with information from Untappd.
    def handle(self, *args, **options):
        updated = 0

        # First priority, recheck prioritized corrected matches
        beers1 = Beer.objects.filter(
            untpd_id__isnull=False, prioritize_recheck=True, active=True
        )
        # Second priority: never updated rating
        beers2 = Beer.objects.filter(
            untpd_id__isnull=False, rating__isnull=True, active=True
        )
        # Third priority: under 500 checkins, but not more often than every 7 day
        time_threshold = timezone.now() - timedelta(days=7)
        beers3 = Beer.objects.filter(
            untpd_updated__lte=time_threshold,
            untpd_id__isnull=False,
            active=True,
            checkins__lte=500,
        )
        # Fourth priority, latest updated rating
        beers4 = Beer.objects.filter(untpd_id__isnull=False, active=True).order_by(
            "untpd_updated"
        )

        # Create list of unique beers (Same beers can appear in different priorities.)
        beers = []
        for x in list(chain(beers1, beers2, beers3, beers4)):
            if x not in beers:
                beers.append(x)

        for beer in beers[: options["calls"]]:
            url = beer.untpd_url
            print(beer.vmp_name + " " + url)

            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                html_page = urlopen(req).read()
                soup = BeautifulSoup(html_page, "lxml")
                data = [
                    json.loads(x.string)
                    for x in soup.find_all("script", type="application/ld+json")
                ]

            except Exception as e:
                print(e)
                break

            beer.untpd_id = (
                data[0]["sku"]
                if data
                else int(
                    soup.find("meta", {"property": "og:url"})["content"].split("/")[-1]
                )
            )
            beer.untpd_name = (
                data[0]["name"]
                if data
                else soup.find("p", {"class": "brewery"}).find("a").text
                + " "
                + soup.find("div", {"class": "name"}).find("h1").text
            )
            beer.brewery = (
                data[0]["brand"]["name"]
                if data
                else soup.find("p", {"class": "brewery"}).find("a").text
            )
            beer.rating = (
                data[0]["aggregateRating"]["ratingValue"]
                if data
                else float(soup.find("div", {"class": "caps"})["data-rating"])
            )
            beer.checkins = (
                data[0]["aggregateRating"]["reviewCount"]
                if data
                else [
                    int(x)
                    for x in re.findall(
                        r"\b\d+\b", soup.find("p", {"class": "raters"}).text
                    )
                ][0]
            )
            beer.style = soup.find("p", {"class": "style"}).text
            beer.description = (
                data[0]["description"]
                if data
                else soup.find(
                    "div", {"class": "beer-descrption-read-less"}
                ).text.strip()
            )
            try:
                beer.abv = [
                    float(x)
                    for x in re.findall(
                        r"\b\d+\b", soup.find("p", {"class": "abv"}).text
                    )
                ][0]
            except Exception:
                beer.abv = 0
            try:
                beer.ibu = [
                    int(x)
                    for x in re.findall(
                        r"\b\d+\b", soup.find("p", {"class": "ibu"}).text
                    )
                ][0]
            except Exception:
                beer.ibu = None
            beer.label_hd_url = soup.find("a", {"class": "label image-big"})[
                "data-image"
            ]
            beer.label_sm_url = soup.find("a", {"class": "label image-big"}).find(
                "img"
            )["src"]
            beer.untpd_url = soup.find("meta", {"property": "og:url"})["content"]
            beer.untpd_updated = timezone.now()
            beer.prioritize_recheck = False
            beer.alcohol_units = (beer.volume * 1000 * beer.abv / 100 * 0.8) / 12
            beer.save()

            updated += 1

        self.stdout.write(
            self.style.SUCCESS(f"Updated {updated} beers out of {options['calls']}")
        )
