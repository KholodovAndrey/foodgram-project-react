from django.contrib import admin

from .models import Subscriptions, User


class UserAdmin(admin.ModelAdmin):
    """Администрирование пользователей."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'date_joined',
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )

    list_filter = (
        'username',
        'email',
        'date_joined',
    )

    ordering = (
        'username',
    )


class SubscriptionsAdmin(admin.ModelAdmin):
    """Администрирование подписок."""

    list_display = (
        'id',
        'user',
        'author',
    )

    search_fields = (
        'user',
        'author',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
