# Generated by Django 4.2.2 on 2023-06-24 14:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Введите уникальный юзернейм', max_length=150, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+\\z$', message='Неверный формат поля')], verbose_name='Имя пользователя'),
        ),
    ]