import pytest, responses
from urllib.parse import quote
from beers.models import Beer, ExternalAPI, MatchFilter
from beers.tasks import smart_update_untappd

@pytest.fixture(autouse=True)
def setup(db):
    ExternalAPI.objects.create(name="untappd", baseurl="https://api.test.com/v4/", api_client_id="123", api_client_secret="321")
    untappd = ExternalAPI.objects.get(name='untappd')
    api_client_id = untappd.api_client_id
    api_client_secret = untappd.api_client_secret
    baseurl = untappd.baseurl

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

@pytest.mark.django_db
@pytest.mark.filterwarnings('ignore::UserWarning')
def test_match_correct_beer(mocked_responses):
    """
    Test that the correct beer matches
    """
    beer = Beer.objects.create(vmp_id=12611502, vmp_name="Ayinger Winterbock", active=True)
    url = "https://api.test.com/v4/search/beer?client_id=123&client_secret=321&q="+quote(beer.vmp_name)+"&limit=5"
    mocked_responses.add(responses.GET, url,
                json={"response":{
                    "beers":{
                        "items":[{
                            "beer":{
                                "bid":1320463,
                                "beer_name":"Ayinger Winter Bock (2015)",
                                "beer_slug":"ayinger-privatbrauerei-ayinger-winter-bock-2015"},
                                "brewery":{
                                    "brewery_name":"Ayinger Privatbrauerei"
                                }
                            },
                            {"beer":{
                                "bid":100415,
                                "beer_name":"Ayinger Winter Bock",
                                "beer_slug":"ayinger-privatbrauerei-ayinger-winter-bock"},
                                "brewery":{
                                    "brewery_name":"Ayinger Privatbrauerei"}
                                }
                        ]}}},
                status=200,
                headers={'X-Ratelimit-Remaining':'10'},
                content_type='application/json'
    )
    
    smart_update_untappd()

    beer = Beer.objects.get(vmp_id=12611502)
    assert beer.untpd_id == 100415
    assert beer.untpd_url == "https://untappd.com/b/ayinger-privatbrauerei-ayinger-winter-bock/100415"

@pytest.mark.django_db
@pytest.mark.filterwarnings('ignore::UserWarning')
def test_no_match(mocked_responses):
    """
    Test that a bad query name will not match
    """
    beer = Beer.objects.create(vmp_id=12630102, vmp_name="Poppels x Sudden Death Behind The Mask NEIPA", active=True)
    query = "Poppels Death Behind The Mask NEIPA"
    url = "https://api.test.com/v4/search/beer?client_id=123&client_secret=321&q="+quote(query)+"&limit=5"
    mocked_responses.add(responses.GET, url,
                json={"response":{
                    "beers":{
                        "items":[]
                        }
                    }
                },
                status=200,
                headers={'X-Ratelimit-Remaining':'10'},
                content_type='application/json'
    )
    
    smart_update_untappd()

    beer = Beer.objects.get(vmp_id=12630102)
    assert beer.untpd_id == None
    assert beer.match_manually == True

@pytest.mark.django_db
@pytest.mark.filterwarnings('ignore::UserWarning')
def test_bad_match(mocked_responses):
    """
    Test that a low Levenshtein distance will not match
    """
    beer = Beer.objects.create(vmp_id=12512002, vmp_name="Buxton Single", active=True)
    query = "Poppels Death Behind The Mask NEIPA"
    url = "https://api.test.com/v4/search/beer?client_id=123&client_secret=321&q="+quote(beer.vmp_name)+"&limit=5"
    mocked_responses.add(responses.GET, url,
                json={"response":{
                    "beers":{
                        "items":[{
                            "beer":{
                                "bid":1537674,
                                "beer_name":"Single Barrel Rain Shadow (Bourbon)",
                                "beer_slug":"buxton-brewery-single-barrel-rain-shadow-bourbon"},
                                "brewery":{
                                    "brewery_name":"Buxton Brewery"
                                }
                            },
                            {"beer":{
                                "bid":3305869,
                                "beer_name":"Single Barrel Rain Shadow 2019",
                                "beer_slug":"buxton-brewery-single-barrel-rain-shadow-2019"},
                                "brewery":{
                                    "brewery_name":"Buxton Brewery"}
                                }
                        ]}}},
                status=200,
                headers={'X-Ratelimit-Remaining':'10'},
                content_type='application/json'
    )
    
    smart_update_untappd()

    beer = Beer.objects.get(vmp_id=12512002)
    assert beer.untpd_id == None
    assert beer.match_manually == True

@pytest.mark.django_db
@pytest.mark.filterwarnings('ignore::UserWarning')
@responses.activate
def test_remove_collab_brewery():
    """
    Test that the matching algorithm successfully removes collaboration brewery from query
    to match the naming style of Vinmonopolet
    """
    Beer.objects.create(vmp_id=12511702, vmp_name="Põhjala x Verdant Wind Forecast", active=True)
    smart_update_untappd()
    
    assert responses.calls[0].request.url == 'https://api.test.com/v4/search/beer?client_id=123&client_secret=321&q=P%C3%B5hjala%20Wind%20Forecast&limit=5'

@pytest.mark.django_db
@pytest.mark.filterwarnings('ignore::UserWarning')
@responses.activate
def test_remove_beer_type():
    """
    Test that the matching algorithm successfully removes beer type from query
    to match the naming style of Vinmonopolet
    """
    Beer.objects.create(vmp_id=10346602, vmp_name="De Tvende No excuses, all apologies New England IPA", active=True)
    MatchFilter.objects.create(name="ipa")
    MatchFilter.objects.create(name="new england ipa")
    smart_update_untappd()

    assert responses.calls[0].request.url == 'https://api.test.com/v4/search/beer?client_id=123&client_secret=321&q=De%20Tvende%20No%20excuses%2C%20all%20apologies&limit=5'