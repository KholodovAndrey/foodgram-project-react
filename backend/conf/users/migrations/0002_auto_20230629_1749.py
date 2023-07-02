from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='auth_token',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_subscribed',
        ),
    ]
