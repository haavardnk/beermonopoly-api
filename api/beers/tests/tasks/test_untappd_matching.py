import pytest, responses
from urllib.parse import quote
from beers.models import Beer, ExternalAPI
from beers.tasks import match_untpd


def create_query_url(query):
    return (
        "https://api.test.com/v4/search/beer?client_id=123&client_secret=321&q="
        + quote(query)
        + "&limit=5"
    )


@pytest.fixture(autouse=True)
def setup(db):
    ExternalAPI.objects.create(
        name="untappd",
        baseurl="https://api.test.com/v4/",
        api_client_id="123",
        api_client_secret="321",
    )


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.mark.django_db
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_match_correct_beer(mocked_responses):
    """
    Test that the correct beer matches
    """
    beer = Beer.objects.create(
        vmp_id=12611502, vmp_name="Ayinger Winterbock", active=True
    )

    mocked_responses.add(
        responses.GET,
        create_query_url(beer.vmp_name),
        json={
            "response": {
                "beers": {
                    "items": [
                        {
                            "beer": {
                                "bid": 1320463,
                                "beer_name": "Ayinger Winter Bock (2015)",
                                "beer_slug": "ayinger-privatbrauerei-ayinger-winter-bock-2015",
                            },
                            "brewery": {"brewery_name": "Ayinger Privatbrauerei"},
                        },
                        {
                            "beer": {
                                "bid": 100415,
                                "beer_name": "Ayinger Winter Bock",
                                "beer_slug": "ayinger-privatbrauerei-ayinger-winter-bock",
                            },
                            "brewery": {"brewery_name": "Ayinger Privatbrauerei"},
                        },
                    ]
                }
            }
        },
        status=200,
        headers={"X-Ratelimit-Remaining": "10"},
        content_type="application/json",
    )

    match_untpd()

    beer = Beer.objects.get(vmp_id=12611502)
    assert beer.untpd_id == 100415
    assert (
        beer.untpd_url
        == "https://untappd.com/b/ayinger-privatbrauerei-ayinger-winter-bock/100415"
    )


@pytest.mark.django_db
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_no_match(mocked_responses):
    """
    Test that a bad query name will not match
    """
    beer = Beer.objects.create(
        vmp_id=12630102,
        vmp_name="Poppels x Sudden Death Behind The Mask NEIPA",
        active=True,
    )
    queries = [
        "Poppels Death Behind The Mask NEIPA",
        "Poppels Death Behind The Mask",
        "Poppels Death Behind The",
        "Poppels Death Behind",
        "Poppels Death",
    ]

    for query in queries:
        mocked_responses.add(
            responses.GET,
            create_query_url(query),
            json={"response": {"beers": {"items": []}}},
            status=200,
            headers={"X-Ratelimit-Remaining": "10"},
            content_type="application/json",
        )

    match_untpd()

    beer = Beer.objects.get(vmp_id=12630102)
    assert beer.untpd_id == None
    assert beer.match_manually == True


@pytest.mark.django_db
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_bad_match(mocked_responses):
    """
    Test that a low Levenshtein distance will not match
    """
    beer = Beer.objects.create(vmp_id=12512002, vmp_name="Buxton Single", active=True)

    mocked_responses.add(
        responses.GET,
        create_query_url(beer.vmp_name),
        json={
            "response": {
                "beers": {
                    "items": [
                        {
                            "beer": {
                                "bid": 1537674,
                                "beer_name": "Single Barrel Rain Shadow (Bourbon)",
                                "beer_slug": "buxton-brewery-single-barrel-rain-shadow-bourbon",
                            },
                            "brewery": {"brewery_name": "Buxton Brewery"},
                        },
                        {
                            "beer": {
                                "bid": 3305869,
                                "beer_name": "Single Barrel Rain Shadow 2019",
                                "beer_slug": "buxton-brewery-single-barrel-rain-shadow-2019",
                            },
                            "brewery": {"brewery_name": "Buxton Brewery"},
                        },
                    ]
                }
            }
        },
        status=200,
        headers={"X-Ratelimit-Remaining": "10"},
        content_type="application/json",
    )

    match_untpd()

    beer = Beer.objects.get(vmp_id=12512002)
    assert beer.untpd_id == None
    assert beer.match_manually == True


@pytest.mark.django_db
@pytest.mark.filterwarnings("ignore::UserWarning")
@responses.activate
def test_remove_collab_brewery():
    """
    Test that the matching algorithm successfully removes collaboration brewery from query
    to match the naming style of Vinmonopolet
    """
    Beer.objects.create(
        vmp_id=12511702, vmp_name="Põhjala x Verdant Wind Forecast", active=True
    )
    match_untpd()

    assert (
        responses.calls[0].request.url
        == "https://api.test.com/v4/search/beer?client_id=123&client_secret=321&q=P%C3%B5hjala%20Wind%20Forecast&limit=5"
    )


@pytest.mark.django_db
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_stop_when_no_api_calls_remaining(mocked_responses):
    """
    Tests that the algorithm stops when only 5 api calls left
    """
    Beer.objects.create(vmp_id=12611502, vmp_name="Ayinger Winterbock", active=True)
    Beer.objects.create(vmp_id=12512002, vmp_name="Ayinger Winterbock", active=True)
    query = "Ayinger Winterbock"

    mocked_responses.add(
        responses.GET,
        create_query_url(query),
        json={
            "response": {
                "beers": {
                    "items": [
                        {
                            "beer": {
                                "bid": 1320463,
                                "beer_name": "Ayinger Winter Bock (2015)",
                                "beer_slug": "ayinger-privatbrauerei-ayinger-winter-bock-2015",
                            },
                            "brewery": {"brewery_name": "Ayinger Privatbrauerei"},
                        }
                    ]
                }
            }
        },
        status=200,
        headers={"X-Ratelimit-Remaining": "5"},
        content_type="application/json",
    )

    match_untpd()

    beer1 = Beer.objects.get(vmp_id=12611502)
    beer2 = Beer.objects.get(vmp_id=12512002)

    assert beer1.untpd_id == 1320463
    assert beer2.untpd_id == None
