from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0002_add_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='subscriptions',
            field=models.ManyToManyField(blank=True, null=True, related_name='subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='Subscriptions'),
        ),
    ]
