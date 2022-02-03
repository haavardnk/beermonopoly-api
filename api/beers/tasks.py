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


def update_stock_from_vmp(stores):
    out = StringIO()
    call_command("update_stock_from_vmp", stores, stdout=out)
    return out.getvalue()


def update_stores_from_csv():
    out = StringIO()
    call_command("update_stores_from_csv", stdout=out)
    return out.getvalue()


def smart_update_untappd():
    # Match if unmatched exists, else update items
    beers = Beer.objects.filter(
        untpd_id__isnull=True, match_manually=False, active=True
    )
    out = StringIO()

    if beers:
        call_command("match_untpd_brute", stdout=out)
    else:
        call_command("update_beers_from_untpd", stdout=out)

    return out.getvalue()


def deactivate_inactive(days):
    out = StringIO()
    call_command("deactivate_inactive", days, stdout=out)
    return out.getvalue()


def get_unreleased_beers_from_vmp():
    out = StringIO()
    call_command("get_unreleased_beers_from_vmp", stdout=out)
    return out.getvalue()


def get_user_checkins(user, id=None):
    out = StringIO()
    if id:
        call_command("get_user_checkins", user, max_id=id, stdout=out)
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


def create_badges_vmp():
    out = StringIO()
    call_command("create_badges_vmp", stdout=out)
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


def add_release(products, badge_text, badge_type, days):
    out = StringIO()
    call_command(
        "add_release",
        products=products,
        badge_text=badge_text,
        badge_type=badge_type,
        days=days,
        stdout=out,
    )
    return out.getvalue()


def update_checkin_matches():
    out = StringIO()
    call_command("update_checkin_matches", stdout=out)
    return out.getvalue()


def get_all_users_wishlist():
    out = StringIO()
    call_command("get_all_users_wishlist", stdout=out)
    return out.getvalue()
