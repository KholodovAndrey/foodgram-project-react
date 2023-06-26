from csv import DictReader

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Скрипт для импорта данных из ingredients.csv"""

    help = 'Загрузка из .csv'

    def handle(self, *args, **options):

        header = ['name', 'measurement_unit']

        self.stdout.write('Загрузка данных')
        file = DictReader(
            open(
                '/Users/andrew/Dev/foodgram-project-react/data/ingredients.csv',
                encoding='utf-8'
            ),
            fieldnames=header
        )
        for row in file:
            data = Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            data.save()
        self.stdout.write('Загрузка данных завершена')
