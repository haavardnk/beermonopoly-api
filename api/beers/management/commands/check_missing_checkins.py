import requests
import json
from beers.models import ExternalAPI, Checkin
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialToken
from django.utils import timezone
from django_q.models import Schedule


class Command(BaseCommand):
    # Checks if users are missing checkins in the database.
    def handle(self, *args, **options):
        untappd = ExternalAPI.objects.get(name="untappd")
        baseurl = untappd.baseurl

        users = User.objects.all().exclude(id=1)

        checked = 0
        scheduled = 0
        failed = 0

        for user in users:
            print("Checking: " + user.username)
            untappd_token = SocialToken.objects.get(
                account__user=user, account__provider="untappd"
            ).token
            loaded_checkins = len(Checkin.objects.filter(user=user))

            url = (
                baseurl
                + "user/info/"
                + "?access_token="
                + untappd_token
                + "&compact=true"
            )

            try:
                headers = {"User-Agent": "django:Beermonopoly"}
                request = requests.get(url, headers=headers)
                response = json.loads(request.text)

                total_checkins = response["response"]["user"]["stats"]["total_checkins"]

                checked += 1

                if (total_checkins > loaded_checkins + 50) or (
                    total_checkins > loaded_checkins + loaded_checkins * 0.05
                    and total_checkins > loaded_checkins + 10
                ):
                    print(
                        "Scheduling update of "
                        + user.username
                        + ", missing "
                        + str(total_checkins - loaded_checkins)
                        + " checkins."
                    )
                    Schedule.objects.create(
                        name="Update checkins of:"
                        + user.username
                        + ". Missing "
                        + str(total_checkins - loaded_checkins)
                        + " checkins.",
                        func="beers.tasks.get_user_checkins",
                        args=str(user.id),
                        schedule_type=Schedule.ONCE,
                        next_run=timezone.now(),
                    )

                    scheduled += 1

            except Exception:
                print("Failed user: " + user.username)
                failed += 1
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Checked {checked} users, scheduled {scheduled} updates, failed to check {failed} users."
            )
        )
