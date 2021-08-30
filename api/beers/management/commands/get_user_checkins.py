import requests, json
from beers.models import Beer, ExternalAPI, Checkin
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialToken


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("user", type=int)

    # Updates the database with information from Untappd.
    def handle(self, *args, **options):
        untappd = ExternalAPI.objects.get(name="untappd")
        baseurl = untappd.baseurl

        user = User.objects.get(id=options["user"])
        untappd_token = SocialToken.objects.get(
            account__user=user, account__provider="untappd"
        ).token

        api_remaining = "100"
        updated = 0
        created = 0
        failed = 0

        url = (
            baseurl + "user/checkins/" + "?access_token=" + untappd_token + "&limit=50"
        )

        while int(api_remaining) >= 5:
            try:
                request = requests.get(url)
                response = json.loads(request.text)
                for checkin in response["response"]["checkins"]["items"]:
                    try:
                        c = Checkin.objects.get(checkin_id=checkin["checkin_id"])
                        c.checkin_id = checkin["checkin_id"]
                        c.user = user
                        c.rating = checkin["rating_score"]
                        c.checkin_url = (
                            "https://untappd.com/user/"
                            + checkin["user"]["user_name"]
                            + "/"
                            + "checkin/"
                            + str(checkin["checkin_id"])
                        )
                        c.save()
                        c.beer.set(
                            Beer.objects.filter(
                                untpd_id=checkin["beer"]["bid"], active=True
                            )
                        )

                        updated += 1

                    except Checkin.DoesNotExist:
                        beers = Beer.objects.filter(
                            untpd_id=checkin["beer"]["bid"], active=True
                        )
                        if beers:
                            c = Checkin.objects.create(
                                checkin_id=checkin["checkin_id"],
                                user=user,
                                rating=checkin["rating_score"],
                                checkin_url="https://untappd.com/user/"
                                + checkin["user"]["user_name"]
                                + "/"
                                + "checkin/"
                                + str(checkin["checkin_id"]),
                            )
                            c.beer.set(beers)
                            created += 1
                        else:
                            continue
                    except:
                        failed += 1
                        continue

                if response["response"]["pagination"]["next_url"]:
                    url = (
                        baseurl
                        + "user/checkins/"
                        + "?access_token="
                        + untappd_token
                        + "&limit=50"
                        + "&max_id="
                        + str(response["response"]["pagination"]["max_id"])
                    )
                else:
                    print("No more pages")
                    break

                api_remaining = request.headers["X-Ratelimit-Remaining"]
                print(api_remaining)

            except:
                break

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated}, created {created} and failed {failed} checkins for user {user}. {api_remaining} api calls remaining"
            )
        )