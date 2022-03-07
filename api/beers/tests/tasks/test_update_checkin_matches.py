import pytest
from pytest_django.asserts import assertQuerysetEqual
from beers.models import Beer, Checkin
from django.contrib.auth.models import User
from beers.tasks import update_checkin_matches


@pytest.fixture(autouse=True)
def setup(db):
    user = User.objects.create(id=1, username="testuser")

    Checkin.objects.create(user=user, checkin_id=12345, untpd_id=123)
    Checkin.objects.create(user=user, checkin_id=23456, untpd_id=333)
    Checkin.objects.create(user=user, checkin_id=34567, untpd_id=234)

    Beer.objects.create(
        vmp_id=12611502,
        vmp_name="Ayinger Winterbock",
        untpd_id=123,
        active=True,
    )
    Beer.objects.create(
        vmp_id=14194601,
        vmp_name="Mold Sider Gaustad",
        untpd_id=234,
        active=True,
    )
    Beer.objects.create(
        vmp_id=13863804,
        vmp_name="Mjøderiet Maple Temptation",
        untpd_id=234,
        active=True,
    )


@pytest.mark.django_db
def test_update_checkin_matches():
    """
    Test that checkin matches gets updated correctly.
    """
    update_checkin_matches(3)
    assertQuerysetEqual(
        Checkin.objects.get(checkin_id=12345).beer.all(),
        Beer.objects.filter(untpd_id=123),
    )
    assertQuerysetEqual(
        Checkin.objects.get(checkin_id=23456).beer.all().order_by("untpd_id"),
        Beer.objects.filter(untpd_id=333).order_by("untpd_id"),
    )
    assertQuerysetEqual(
        list(Checkin.objects.get(checkin_id=34567).beer.all()),
        list(Beer.objects.filter(untpd_id=234)),
    )
