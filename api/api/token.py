from allauth.headless.tokens.sessions import SessionTokenStrategy
from rest_framework.authtoken.models import Token


class AccessTokenStrategy(SessionTokenStrategy):
    def create_access_token(self, request):
        user = request.user
        token = Token.objects.get_or_create(user=user)
        return token[0].key
