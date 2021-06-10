from django.core import management
from beers.models import Beer


def update_beers_from_vmp():
    return management.call_command("update_beers_from_vmp")


def match_untpd():
    return management.call_command("match_untpd")


def update_beers_from_untpd():
    return management.call_command("update_beers_from_untpd")


def update_stock_from_vmp():
    return management.call_command("update_stock_from_vmp")


def update_stores_from_csv():
    return management.call_command("update_stores_from_csv")


def smart_update_untappd():
    # Match if unmatched exists, else update items
    beers = Beer.objects.filter(untpd_id__isnull=True, match_manually=False)

    if beers:
        return management.call_command("match_untpd")
    else:
        return management.call_command("update_beers_from_untpd")


def deactivate_inactive():
    return management.call_command("deactivate_inactive")
