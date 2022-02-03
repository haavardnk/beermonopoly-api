import requests, json
from beers.models import Beer, ExternalAPI, Wishlist
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialToken


class Command(BaseCommand):

    # Updates the database with information from Untappd.
    def handle(self, *args, **options):

        untappd = ExternalAPI.objects.get(name="untappd")
        baseurl = untappd.baseurl

        users = User.objects.all().exclude(id=1)

        added = 0
        created_list = 0
        failed = 0

        for user in users:
            print(user)
            untappd_token = SocialToken.objects.get(
                account__user=user, account__provider="untappd"
            ).token

            count = 0

            url = (
                baseurl
                + "user/wishlist/"
                + "?access_token="
                + untappd_token
                + "&limit=50"
            )

            wishlist = Wishlist.objects.filter(user=user)
            if wishlist:
                wishlist[0].beer.clear()
                wishlist[0].save()

            while True:
                print("Retrieving")
                try:
                    headers = {"User-Agent": "django:Beermonopoly"}
                    request = requests.get(url, headers=headers)
                    response = json.loads(request.text)
                    for wish in response["response"]["beers"]["items"]:
                        try:
                            beers = Beer.objects.filter(untpd_id=wish["beer"]["bid"])
                            if beers:
                                wishlist = Wishlist.objects.get(user=user)

                                for beer in beers:
                                    wishlist.beer.add(beer.vmp_id)

                                wishlist.save()
                                added += 1

                            count += 1

                        except Wishlist.DoesNotExist:
                            wishlist = Wishlist.objects.create(user=user)
                            beers = Beer.objects.filter(untpd_id=wish["beer"]["bid"])
                            if beers:
                                for beer in beers:
                                    wishlist.beer.add(beer.vmp_id)

                                wishlist.save()
                                added += 1

                            count += 1
                            created_list += 1

                        except Exception as e:
                            print(e)
                            count += 1
                            failed += 1
                            continue
                    if response["response"]["total_count"] > count:
                        url = (
                            baseurl
                            + "user/wishlist/"
                            + "?access_token="
                            + untappd_token
                            + "&limit=50"
                            + "&offset="
                            + str(count)
                        )
                    else:
                        print("No more pages")
                        break

                except:
                    break

        self.stdout.write(
            self.style.SUCCESS(
                f"Added {added}, failed {failed}, created lists {created_list} for {users.count()} users."
            )
        )
