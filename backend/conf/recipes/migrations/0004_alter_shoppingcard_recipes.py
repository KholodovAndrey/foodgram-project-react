from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_subscription_subscriptions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcard',
            name='recipes',
            field=models.ManyToManyField(blank=True, related_name='recipes', to='recipes.Recipe', verbose_name='Recipes'),
        ),
    ]
