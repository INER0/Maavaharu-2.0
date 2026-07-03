from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Validates sign-up data and creates a new user with a hashed password."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'phone']

    def create(self, validated_data):
        # create_user hashes the password; never store raw passwords.
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Checks a username/password pair and returns the user if correct."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid username or password.')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Used by admins to list/manage accounts, and to show 'who am I'."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'is_active']
