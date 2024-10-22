from django.views.generic import TemplateView


class EmailConfirmedTemplateView(TemplateView):
    template_name = "email_confirmed.html"
