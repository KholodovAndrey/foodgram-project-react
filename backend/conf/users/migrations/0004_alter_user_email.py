from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20230629_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(
                max_length=254,
                unique=True,
                verbose_name='email address'
            ),
        ),
    ]
