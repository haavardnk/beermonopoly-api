from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Create your views here.


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
