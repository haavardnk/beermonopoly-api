from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from notifications.models import FCMToken


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_token(request):
    token = request.query_params.get("token", None)
    if token is not None:
        try:
            fcm_token = FCMToken.objects.get(user=request.user)

            fcm_token.token = token
            fcm_token.save()

            message = {"message": f"FCM token updated for user {request.user.username}"}

            return Response(message, status=200)

        except FCMToken.DoesNotExist:
            FCMToken.objects.create(user=request.user, token=token)
            message = {"message": f"FCM token created for user {request.user.username}"}

            return Response(message, status=200)

        except:
            message = {"message": "An error occurred"}
            return Response(message, status=500)
    else:
        message = {"message": "beer_id missing"}
        return Response(message, status=400)
