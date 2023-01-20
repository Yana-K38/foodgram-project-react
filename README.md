# Дипломный проект foodgram-project-react

![example workflow](https://github.com/yana-k38/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Описание

Foodgram - Продуктовый помощник. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Проект развернут по адресу

- http://158.160.49.35/
- http://158.160.49.35/admin/
Учетная запись администратора:
  логин: admin
  пароль: admin
- http://158.160.49.35/api/docs/

### Инструкция по развертыванию проекта.

1. Клонируйте репозиторий:
```
git clone github.com/Yana-K38/foodgram-project-react
```
2. Создать файл .env в папке проекта /infra/ и заполнить его всеми ключами:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
3. Собрать контейнеры:
```
cd foodgram-project-react/infra
docker-compose up -d --build
```
4. Сделать миграции, собрать статику и создать суперпользователя:
```
docker-compose exec  backend python manage.py makemigrations users --noinput
docker-compose exec  backend python manage.py makemigrations recipes --noinput
docker-compose exec  backend python manage.py migrate --noinput
docker-compose exec  backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py createsuperuser
```
Для заполнения базы данных начальными данными списка ингридиетов выполните:
```
docker-compose exec backend python manage.py load_ingredients
```
##### После запуска проекта, документация будет доступна по адресу:
```http://localhost/api/docs/redoc.html```


### Несколько примеров запросов к API.
регистрация пользователя
POST-запрос: /api/users/
Request sample:
```
{

    "email": "string",
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "password": "string"

}
```

Request sample(201):
```
{

  "email": "string",
    "id": 0,
    "username": "string",
    "first_name": "string",
    "last_name": "string"

}
```
Response sample (400):
```
{
    «field_name»: [
      «Обязательное поле.»
    ]
}
```
Получение токена
POST-запрос: /api/auth/token/login/
Request sample:
```
{
    «email»: «string»,
    «password»: «string»
}
```
Response sample (201):
```
{
    «token»: «string»
}
```
Response sample (400):
```
{
   «field_name»: [
      «string»
    ]
}
```

