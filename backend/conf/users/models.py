from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Модель пользователя."""

    first_name = models.CharField(_('first name'), max_length=150, blank=False,
                                  null=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False,
                                 null=False)
    email = models.EmailField(_('email address'), blank=False, null=False,
                              unique=True)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
