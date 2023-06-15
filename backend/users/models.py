from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    firstname = models.CharField(
        verbose_name='Имя',
        max_length=100,
        unique=False,
        help_text='Введите имя'
    )

    lastname = models.CharField(
        verbose_name='Фамилия',
        max_length=100,
        unique=False,
        help_text='Введите фамилию',
    )

    username = models.CharField(
        verbose_name='Логин',
        max_length=100,
        unique=True,
        help_text='Введите имя пользователя',
    )

    email = models.EmailField(
        verbose_name='Эл. почта',
        max_length=150,
        unique=True,
        help_text='Введите эл. почту',
        null=False,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follows(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author'
    )
    constrains = [
        models.UniqueConstraint(
            fields=['user', 'author'], name='unique_following'
        )
    ]

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
