from rest_framework.permissions import BasePermission


class RecipePermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if view.action in ['download_shopping_cart']:
            return user and user.is_authenticated and user.is_active
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['PATCH', 'DELETE']:
            return request.user == obj.author
        return True
