# Generated by Django 3.2.19 on 2023-07-08 15:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', 'add_ingredients'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='subscriptions',
        ),
        migrations.AddField(
            model_name='subscription',
            name='subscriptions',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='Подписки'),
        ),
    ]
