from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from .forms import VisitorSignUpForm
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .permissions import IsAdmin


def signup_page(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = VisitorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your Maavaharu account has been created.')
            return redirect('home')
    else:
        form = VisitorSignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Welcome back to Maavaharu.')
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


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
