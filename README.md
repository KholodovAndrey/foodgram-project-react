# FOODGRAM
![example workflow](https://github.com/KholodovAndrey/foodgram-project-react/actions/workflows/foodgram_actions.yml/badge.svg)

http://foodgram-diplom.ddns.net/
login: aholodov3@mail.ru  
password: QAZwsx12  

## О проекте

Проект представляет собой веб-сайт для постинга и просмотра рецептов различных блюд.

Функциональность сайта:
- Просмотр списка рецептов
- Просмотр деталей рецепта
- Создание и редактирование своих рецептов
- Сортировка рецептов по тегам
- Аутентификация и авторизация пользователей
- Подписка на других пользователей
- Формирование списка избранных рецептов
- Формирование и выгрузка списка продуктов

## Установка
Перед установкой обновите индекс пакетов APT:
   ```
   sudo apt update
   ```

1. Клонируйте репозиторий:
   ```
   git clone git@github.com:KholodovAndrey/foodgram-project-react.git
   ```

2. Установите Docker и Docker-compose:
   ```
   sudo apt install docker.io
   sudo apt install docker-compose
   ```

3. Установите инструменты для работы с Postgres:
   ```
   sudo apt install postgresql postgresql-contrib -y
   ```

4. На своем сервере создайте директорию infra, в которуюнадо скопировать файлы развертывания инфраструктуры:

   ```
   docker-compose.yml
   nginx.conf
   ```

5. В этой же директории создайте файл виртуального окружения:

   ```
   touch .env
   ```
   со следующими параметрами:
   ```
   SECRET_KEY = django-insecure-8#*@yr8r=0d-z5%#db$c&=y#ub4bzux5q)+h&w*yld61mlm^#n
   POSTGRES_DB=django.db.backends.postgresql
   DB_NAME=foodgram
   POSTGRES_USER=foodgramadmin
   POSTGRES_PASSWORD=foodgrampassword
   DB_HOST=db
   DB_PORT=5432
   ```

5. Запустите контениризацию:

   ```
   docker-compose up
   ```
6. Миграции
7. Коллектстатик
8. Локалхост

## Использование

----------------------------------------------------------------

## Технологии

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

## Авторы

- Андрей Холодов (https://github.com/KholodovAndrey)
