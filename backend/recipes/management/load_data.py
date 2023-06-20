import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

DATA_FILE_PATH = Path(
    Path(BASE_DIR, 'data/'),
    'ingredients.csv'
)


class Command(BaseCommand):
    """Скрипт для импорта данных из ingredients.csv"""

    help = 'Загрузка из .csv'

    def handle(self, *args, **options):

        header = ['name', 'measurement_unit']

        if Ingredient.objects.exists():
            self.stderr.write('Данные уже присутствуют.')
            return

        self.stdout.write('Загрузка данных')
        file = csv.DictReader(
            open(DATA_FILE_PATH, encoding='utf-8'),
            fieldnames=header
        )
        for row in file:
            data = Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            data.save()
