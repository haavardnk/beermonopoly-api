import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.http import HttpResponseRedirect


class HttpResponseTemporaryRedirect(HttpResponseRedirect):
    status_code = 307
    allowed_schemes = ["intent"]


class DeleteAccount(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            user = self.request.user
            user.delete()

            message = {"message": "User deleted"}
            return Response(message, status=200)
        except:
            message = {"message": "Failed to delete user"}
        return Response(message, status=400)


@api_view(["POST"])
def apple_signin_callback(request) -> HttpResponseTemporaryRedirect:
    args = request.body.decode("utf-8")
    package = os.getenv("APPLE_AUTH_CLIENT_ID_ANDROID")
    redirect = (
        f"intent://callback?{args}#Intent;package={package};scheme=signinwithapple;end"
    )

    return HttpResponseTemporaryRedirect(redirect_to=redirect)
