import os

from django.db import migrations
from rest_framework.utils import json


def add_ingredients(apps, schema_editor):
    ingredient = apps.get_model('recipes', 'Ingredient')
    path = os.path.join(os.path.dirname(__file__),
                        '..', '..', '..', '..', 'data', 'ingredients.json')
    with open(path, 'r') as file:
        data = json.load(file)
        for item in data:
            ingredient.objects.create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0002_initial'),
    ]
    operations = [
        migrations.RunPython(add_ingredients),
    ]