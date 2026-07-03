"""Reusable permission classes that check a user's role.

A DRF permission class answers one question: 'is this user allowed to make
this request?' It returns True (allow) or False (deny -> 403)."""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN


class IsHotelManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.HOTEL_MANAGER


class IsFerryOperator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.FERRY_OPERATOR


class IsThemeParkStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.THEMEPARK_STAFF


class ReadOnlyOrStaff(BasePermission):
    """Anyone logged in may read (GET/HEAD/OPTIONS). Only the staff role passed
    in `view.manager_roles` may create/edit/delete."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        allowed = getattr(view, 'manager_roles', [])
        return request.user.is_authenticated and (
            request.user.role in allowed or request.user.role == User.Role.ADMIN
        )
