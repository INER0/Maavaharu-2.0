from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .permissions import IsAdmin


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ -> create a new account (open to anyone)."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    """POST /api/auth/login/ -> returns an auth token to use on later requests."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        })


class MeView(APIView):
    """GET /api/auth/me/ -> details of the currently logged-in user."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    """Admin-only management of all user accounts (list, edit, deactivate)."""
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
