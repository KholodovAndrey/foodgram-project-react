# FOODGRAM
![example workflow](https://github.com/KholodovAndrey/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)

## О проекте

Проект представляет собой веб-сайт для постинга и просмотра рецептов различных блюд.

Функциональность сайта:
- Просмотр списка рецептов
- Просмотр деталей рецепта
- Создание, редактирование и удаление своих рецептов
- Возможность добавления тегов для рецепта
- Поиск рецептов по названию и/или тегам
- Аутентификация и авторизация пользователей
- Подписка на других пользователей
- Формирование списка избранных рецептов
- Формирование и выгрузка списка продуктов

## Установка

1. Клонируйте репозиторий:

   ```
   git clone git@github.com:KholodovAndrey/foodgram-project-react.git
   ```

2. Создайте виртуальное окружение и активируйте его:

   ```
   python -m venv env
   source env/bin/activate
   ```

3. Установите зависимости:

   ```
   pip install -r requirements.txt
   ```

4. Создайте миграции:

   ```
   python manage.py makemigrations
   ```

5. Выполните миграции:

   ```
   python manage.py migrate
   ```

5. Запустите локальный сервер:

   ```
   python manage.py runserver
   ```

## Использование

----------------------------------------------------------------

## Технологии

 **Python 3.9,
 [Django 3](https://docs.djangoproject.com/en/3.0/),
 [DjangoRestFramework](https://www.django-rest-framework.org),
 [PostgreSQL](https://www.postgresql.org/docs/)

## Авторы

- Андрей Холодов (https://github.com/KholodovAndrey)
