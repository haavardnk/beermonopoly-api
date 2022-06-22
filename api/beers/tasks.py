from django.core.management import call_command
from io import StringIO
from beers.models import Beer


def update_beers_from_vmp():
    out = StringIO()
    call_command("update_beers_from_vmp", stdout=out)
    return out.getvalue()


def match_untpd():
    out = StringIO()
    call_command("match_untpd_brute", stdout=out)
    return out.getvalue()


def update_beers_from_untpd():
    out = StringIO()
    call_command("update_beers_from_untpd", stdout=out)
    return out.getvalue()


def update_details_from_vmp(calls):
    out = StringIO()
    call_command("update_details_from_vmp", calls, stdout=out)
    return out.getvalue()


def update_stock_from_vmp(stores):
    out = StringIO()
    call_command("update_stock_from_vmp", stores, stdout=out)
    return out.getvalue()


def update_stores_from_csv():
    out = StringIO()
    call_command("update_stores_from_csv", stdout=out)
    return out.getvalue()


def smart_update_untappd(**kwargs):
    access_token = kwargs.get("token", None)

    # Match if unmatched exists, else update items
    beers = Beer.objects.filter(
        untpd_id__isnull=True, match_manually=False, active=True
    )
    out = StringIO()

    if beers:
        if access_token is not None:
            call_command("match_untpd_brute", access_token, stdout=out)
        else:
            call_command("match_untpd_brute", stdout=out)
    else:
        if access_token is not None:
            call_command("update_beers_from_untpd", access_token, stdout=out)
        else:
            call_command("update_beers_from_untpd", stdout=out)

    return out.getvalue()


def get_users_friendlist(user=None, full=False):
    out = StringIO()

    if user is not None:
        call_command("get_users_friendlist", user, full=full, stdout=out)
    else:
        call_command("get_users_friendlist", full=full, stdout=out)

    return out.getvalue()


def deactivate_inactive(days):
    out = StringIO()
    call_command("deactivate_inactive", days, stdout=out)
    return out.getvalue()


def get_unreleased_beers_from_vmp():
    out = StringIO()
    call_command("get_unreleased_beers_from_vmp", stdout=out)
    return out.getvalue()


def get_user_checkins(user, max_id=None):
    out = StringIO()
    if max_id:
        call_command("get_user_checkins", user, max_id=max_id, stdout=out)
    else:
        call_command("get_user_checkins", user, stdout=out)
    return out.getvalue()


def get_all_users_last_checkins(loops):
    out = StringIO()
    call_command("get_all_users_last_checkins", loops, stdout=out)
    return out.getvalue()


def remove_match_manually():
    out = StringIO()
    call_command("remove_match_manually", stdout=out)
    return out.getvalue()


def create_badges_untpd():
    out = StringIO()
    call_command("create_badges_untpd", stdout=out)
    return out.getvalue()


def create_badges_custom(products, badge_text, badge_type):
    out = StringIO()
    call_command(
        "create_badges_custom",
        products=products,
        badge_text=badge_text,
        badge_type=badge_type,
        stdout=out,
    )
    return out.getvalue()


def remove_badges(badge_type):
    out = StringIO()
    call_command(
        "remove_badges",
        badge_type,
        stdout=out,
    )
    return out.getvalue()


def add_release(name, products, badge_text, badge_type, days):
    out = StringIO()
    call_command(
        "add_release",
        name=name,
        products=products,
        badge_text=badge_text,
        badge_type=badge_type,
        days=days,
        stdout=out,
    )
    return out.getvalue()


def update_checkin_matches(limit):
    out = StringIO()
    call_command("update_checkin_matches", limit, stdout=out)
    return out.getvalue()


def get_all_users_wishlist():
    out = StringIO()
    call_command("get_all_users_wishlist", stdout=out)
    return out.getvalue()


def create_release(name, products):
    out = StringIO()
    call_command(
        "create_release",
        name=name,
        products=products,
        stdout=out,
    )
    return out.getvalue()
