import pytest
from beers.models import Beer
from beers.tasks import remove_match_manually


@pytest.mark.django_db
def test_remove_match_manually():
    """
    Test that a beer with match manually set to true gets set to false.
    """
    Beer.objects.create(
        vmp_id=12611502,
        vmp_name="Ayinger Winterbock",
        active=True,
        match_manually=True,
    )

    remove_match_manually()

    beer = Beer.objects.get(vmp_id=12611502)
    assert beer.match_manually == False
