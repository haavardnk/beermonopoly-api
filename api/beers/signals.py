from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django_q.models import Schedule
from beers.models import Beer, Checkin
from django.db.models.signals import post_save


@receiver(user_signed_up)
def get_checkins(request, user, **kwargs):

    Schedule.objects.create(
        name="get checkins for user: " + user.username,
        func="beers.tasks.get_user_checkins",
        args=str(user.id),
        schedule_type=Schedule.DAILY,
    )


@receiver(post_save, sender=Beer)
def delete_checkins_for_changed_untappd_id(sender, instance, created, **kwargs):
    if "untpd_id" in instance.get_dirty_fields():
        Checkin.objects.filter(beer=instance).delete()
