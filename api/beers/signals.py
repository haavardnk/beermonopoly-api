from allauth.account.signals import user_signed_up
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.dispatch import receiver
from django_q.models import Schedule
from django.db.models.signals import post_save


@receiver(user_signed_up)
def get_checkins(request, user, **kwargs):

    Schedule.objects.create(
        name="get checkins for user: " + user.username,
        func="beers.tasks.get_user_checkins",
        args=str(user.id),
        schedule_type=Schedule.DAILY,
    )
