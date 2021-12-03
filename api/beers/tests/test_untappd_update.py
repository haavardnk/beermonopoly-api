import pytest, responses
from freezegun import freeze_time
from django.utils import timezone
from beers.models import Beer, ExternalAPI
from beers.tasks import smart_update_untappd


@pytest.fixture(autouse=True)
def setup(db):
    ExternalAPI.objects.create(
        name="untappd",
        baseurl="https://api.test.com/v4/",
        api_client_id="123",
        api_client_secret="321",
    )


@pytest.fixture
def json_response():
    resp = {
        "response": {
            "beer": {
                "bid": 100415,
                "beer_name": "Ayinger Winter Bock",
                "beer_slug": "ayinger-privatbrauerei-ayinger-winter-bock",
                "rating_score": 3.52099,
                "rating_count": 7509,
                "beer_style": "Bock - Doppelbock",
                "beer_description": "Test description",
                "beer_abv": 6.7,
                "beer_ibu": 28,
                "beer_label_hd": "https://api.test.com/site/beer_logos_hd/beer-100415_64d6e_hd.jpeg",
                "brewery": {"brewery_name": "Ayinger Privatbrauerei"},
            }
        }
    }
    return resp


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.mark.django_db
@freeze_time("2020-01-01 03:21:34")
def test_update_beer_correctly(mocked_responses, json_response):
    """
    Test that the beer gets updated correctly
    """
    beer = Beer.objects.create(
        vmp_id=12611502,
        vmp_name="Ayinger Winterbock",
        active=True,
        untpd_id=100415,
        prioritize_recheck=True,
    )

    url = (
        "https://api.test.com/v4/beer/info/"
        + str(beer.untpd_id)
        + "?client_id=123&client_secret=321"
    )
    mocked_responses.add(
        responses.GET,
        url,
        json=json_response,
        status=200,
        headers={"X-Ratelimit-Remaining": "10"},
        content_type="application/json",
    )

    smart_update_untappd()

    beer = Beer.objects.get(vmp_id=12611502)
    assert beer.untpd_name == "Ayinger Winter Bock"
    assert beer.brewery == "Ayinger Privatbrauerei"
    assert beer.rating == pytest.approx(3.52099)
    assert beer.checkins == 7509
    assert beer.style == "Bock - Doppelbock"
    assert beer.description == "Test description"
    assert beer.abv == pytest.approx(6.7)
    assert beer.ibu == 28
    assert (
        beer.label_url
        == "https://api.test.com/site/beer_logos_hd/beer-100415_64d6e_hd.jpeg"
    )
    assert (
        beer.untpd_url
        == "https://untappd.com/b/ayinger-privatbrauerei-ayinger-winter-bock/100415"
    )
    assert beer.untpd_updated == timezone.now()
    assert beer.prioritize_recheck == False


@pytest.mark.django_db
def test_update_beer_no_search_match(mocked_responses):
    """
    Test that the beer does not get updated if there is no search result returned
    """
    beer = Beer.objects.create(
        vmp_id=12611502,
        vmp_name="Ayinger Winterbock",
        active=True,
        untpd_id=100415,
        prioritize_recheck=True,
    )

    url = (
        "https://api.test.com/v4/beer/info/"
        + str(beer.untpd_id)
        + "?client_id=123&client_secret=321"
    )
    mocked_responses.add(
        responses.GET,
        url,
        json={"response": {"beer": {}}},
        status=200,
        headers={"X-Ratelimit-Remaining": "10"},
        content_type="application/json",
    )

    smart_update_untappd()

    beer = Beer.objects.get(vmp_id=12611502)
    assert beer.untpd_name == None


@pytest.mark.django_db
def test_stop_when_no_api_calls_remaining(mocked_responses, json_response):
    """
    Tests that the algorithm stops when only 5 api calls left
    """
    Beer.objects.create(
        vmp_id=12611503, vmp_name="Ayinger Winterbock", active=True, untpd_id=100415
    )
    Beer.objects.create(
        vmp_id=12611504, vmp_name="Ayinger Winterbock", active=True, untpd_id=100415
    )

    url = "https://api.test.com/v4/beer/info/100415?client_id=123&client_secret=321"
    mocked_responses.add(
        responses.GET,
        url,
        json=json_response,
        status=200,
        headers={"X-Ratelimit-Remaining": "5"},
        content_type="application/json",
    )

    smart_update_untappd()

    beer1 = Beer.objects.get(vmp_id=12611503)
    beer2 = Beer.objects.get(vmp_id=12611504)

    assert beer1.untpd_name == "Ayinger Winter Bock"
    assert beer2.untpd_name == None


@pytest.mark.django_db
@responses.activate
def test_break_if_bad_response():
    """
    Tests that the algorithm stops if bad http response is received
    """
    Beer.objects.create(
        vmp_id=12611503, vmp_name="Ayinger Winterbock", active=True, untpd_id=100415
    )
    Beer.objects.create(
        vmp_id=12611504, vmp_name="Ayinger Winterbock", active=True, untpd_id=100415
    )

    smart_update_untappd()

    assert len(responses.calls) == 1
