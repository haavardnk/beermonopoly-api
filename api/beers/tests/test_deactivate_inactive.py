import pytest
from django.utils import timezone
from datetime import timedelta
from beers.models import Beer
from beers.tasks import deactivate_inactive

@pytest.mark.django_db
def test_deactivate_inactive_beer():
    """
    Test that a beer which is no longer on vinmonopolet gets deactivated.
    """
    Beer.objects.create(vmp_id=12611502,
                        vmp_name="Ayinger Winterbock",
                        active=True,
                        vmp_updated=timezone.now() - timedelta(days=31)
                        )

    deactivate_inactive()

    beer = Beer.objects.get(vmp_id=12611502)
    assert beer.active == False

@pytest.mark.django_db
def test_active_beer_does_not_get_deactivated():
    """
    Test that a beer which is active on vinmonopolet does not get deactivated.
    """
    Beer.objects.create(vmp_id=12611502,
                        vmp_name="Ayinger Winterbock",
                        active=True,
                        vmp_updated=timezone.now() - timedelta(days=29)
                        )

    deactivate_inactive()

    beer = Beer.objects.get(vmp_id=12611502)
    assert beer.active == True