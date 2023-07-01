from django.contrib.admin import (ModelAdmin, register)

from . import models


@register(models.User)
class UserAdmin(ModelAdmin):
    list_display = (
        'username', 'pk', 'email', 'password', 'first_name', 'last_name',
    )
    list_editable = ('password', )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name')


# @register(models.Subscribe)
# class SubscribeAdmin(ModelAdmin):
#     list_display = ('pk', 'user', 'author')
