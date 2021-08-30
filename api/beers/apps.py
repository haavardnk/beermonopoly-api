from django.apps import AppConfig


class BeersConfig(AppConfig):
    name = "beers"

    def ready(self):
        import beers.signals
