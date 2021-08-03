from django.core.management import call_command
from io import StringIO
from beers.models import Beer


def update_beers_from_vmp():
    out = StringIO()
    call_command("update_beers_from_vmp", stdout=out)
    return out.getvalue()


def match_untpd():
    out = StringIO()
    call_command("match_untpd", stdout=out)
    return out.getvalue()


def update_beers_from_untpd():
    out = StringIO()
    call_command("update_beers_from_untpd", stdout=out)
    return out.getvalue()


def update_stock_from_vmp():
    out = StringIO()
    call_command("update_stock_from_vmp", stdout=out)
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


def deactivate_inactive():
    out = StringIO()
    call_command("deactivate_inactive", stdout=out)
    return out.getvalue()
