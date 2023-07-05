from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):  # мы переопределяем модель, чтобы сделать поля
                           # обязательными, что значит убираем лишний код?

    """Модель пользователя."""

    first_name = models.CharField(_('Имя'), max_length=150, blank=False,
                                  null=False)
    last_name = models.CharField(_('Фамилия'), max_length=150, blank=False,
                                 null=False)
    email = models.EmailField(_('Электронная почта'), blank=False, null=False,
                              unique=True)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
