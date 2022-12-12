import requests, json
from beers.models import Beer, ExternalAPI, Checkin
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialToken
from datetime import timedelta
from django.utils import timezone
from django_q.models import Schedule


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("loops", type=int)

    # Updates the database with information from Untappd.
    def handle(self, *args, **options):

        untappd = ExternalAPI.objects.get(name="untappd")
        baseurl = untappd.baseurl

        users = User.objects.all().exclude(id=1)

        updated = 0
        created = 0
        failed = 0

        for user in users:
            print(user)
            untappd_token = SocialToken.objects.get(
                account__user=user, account__provider="untappd"
            ).token

            api_remaining = "100"

            url = (
                baseurl
                + "user/checkins/"
                + "?access_token="
                + untappd_token
                + "&limit=50"
            )

            while int(api_remaining) >= options["loops"]:
                try:
                    headers = {"User-Agent": "django:Beermonopoly"}
                    request = requests.get(url, headers=headers)
                    response = json.loads(request.text)
                    for checkin in response["response"]["checkins"]["items"]:
                        try:
                            c = Checkin.objects.get(checkin_id=checkin["checkin_id"])
                            beers = Beer.objects.filter(untpd_id=checkin["beer"]["bid"])

                            c.checkin_id = checkin["checkin_id"]
                            c.untpd_id = checkin["beer"]["bid"]
                            c.user = user
                            c.rating = checkin["rating_score"]
                            c.name = (
                                checkin["brewery"]["brewery_name"]
                                + " "
                                + checkin["beer"]["beer_name"]
                            )
                            c.style = checkin["beer"]["beer_style"]
                            c.abv = checkin["beer"]["beer_abv"]
                            c.checkin_url = (
                                "https://untappd.com/user/"
                                + checkin["user"]["user_name"]
                                + "/"
                                + "checkin/"
                                + str(checkin["checkin_id"])
                            )
                            c.checkin_date = timezone.datetime.strptime(
                                checkin["created_at"], "%a, %d %b %Y %H:%M:%S %z"
                            )
                            c.save()

                            if beers:
                                c.beer.set(beers)

                            updated += 1

                        except Checkin.DoesNotExist:
                            beers = Beer.objects.filter(
                                untpd_id=checkin["beer"]["bid"], active=True
                            )

                            c = Checkin.objects.create(
                                checkin_id=checkin["checkin_id"],
                                untpd_id=checkin["beer"]["bid"],
                                user=user,
                                rating=checkin["rating_score"],
                                name=(
                                    checkin["brewery"]["brewery_name"]
                                    + " "
                                    + checkin["beer"]["beer_name"]
                                ),
                                style=checkin["beer"]["beer_style"],
                                abv=checkin["beer"]["beer_abv"],
                                checkin_url="https://untappd.com/user/"
                                + checkin["user"]["user_name"]
                                + "/"
                                + "checkin/"
                                + str(checkin["checkin_id"]),
                                checkin_date=timezone.datetime.strptime(
                                    checkin["created_at"], "%a, %d %b %Y %H:%M:%S %z"
                                ),
                            )

                            if beers:
                                c.beer.set(beers)

                            created += 1

                        except Exception as e:
                            print(e)
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

            if (
                int(api_remaining) <= 4
                and response["response"]["pagination"]["next_url"]
            ):
                print(
                    "Not enough api calls remaining, scheduling new run in two hours."
                )
                Schedule.objects.create(
                    name="get more checkins for user: " + user.username,
                    func="beers.tasks.get_user_checkins",
                    args=str(user.id)
                    + ","
                    + str(response["response"]["pagination"]["max_id"]),
                    schedule_type=Schedule.ONCE,
                    next_run=timezone.now() + timedelta(hours=2),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated}, created {created} and failed {failed} checkins for {users.count()} users."
            )
        )
