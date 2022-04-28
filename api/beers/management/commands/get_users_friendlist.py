import requests, json
from beers.models import ExternalAPI, FriendList
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialToken


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("user", type=int, nargs="?", default=None)
        parser.add_argument("--full", action="store_true")

    def handle(self, *args, **options):

        untappd = ExternalAPI.objects.get(name="untappd")
        baseurl = untappd.baseurl

        full_update = options["full"]

        if options["user"] is not None:
            users = User.objects.filter(id=options["user"])
        else:
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

            url = baseurl + "user/friends/" + "?access_token=" + untappd_token

            fl = FriendList.objects.filter(user=user)
            if fl:
                fl[0].friend.clear()
                fl[0].save()

            while True:
                try:
                    headers = {"User-Agent": "django:Beermonopoly"}
                    request = requests.get(url, headers=headers)
                    response = json.loads(request.text)
                    for f in response["response"]["items"]:
                        try:
                            friend = User.objects.filter(
                                username=f["user"]["user_name"]
                            )[0]
                            if friend:
                                fl = FriendList.objects.get(user=user)
                                fl.friend.add(friend.id)

                                fl.save()
                                added += 1

                            count += 1

                        except FriendList.DoesNotExist:
                            fl = FriendList.objects.create(user=user)
                            friend = User.objects.filter(
                                username=f["user"]["user_name"]
                            )[0]
                            if friend:
                                fl = FriendList.objects.get(user=user)
                                fl.friend.add(friend.id)

                                fl.save()
                                added += 1

                            count += 1
                            created_list += 1

                        except Exception:
                            count += 1
                            failed += 1
                            continue

                    if (
                        response["response"]["pagination"]["next_url"]
                        and full_update == True
                    ):
                        print(str(count) + " of " + str(response["response"]["found"]))
                        url = (
                            baseurl
                            + "user/friends/"
                            + "?access_token="
                            + untappd_token
                            + "&offset="
                            + str(response["response"]["pagination"]["offset"])
                        )
                    else:
                        print("No more pages")
                        break

                except:
                    break

        self.stdout.write(
            self.style.SUCCESS(
                f"Added {added} friends, {failed} not on Ølmonopolet. Created {created_list} lists for {users.count()} users."
            )
        )
