from rest_framework.permissions import BasePermission


class TokenAuthPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if view.action == 'logout':
            return user and user.is_authenticated and user.is_active
        return True


class UserAuthPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if view.action in ['retrieve', 'me', 'set_password']:
            return user and user.is_authenticated and user.is_active
        return True
