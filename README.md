# Yatube
Yatube - это блог, где пользователи могут создавать посты с картинками, 
подписываться на других пользователей, оставлять комментарии, ставить лайки.

## Технологии и требования
```
Python 3.9+
Django
Django REST Framework
```

## Запуск проекта локально

```
1) Скачать проект с гитхаб
2) Установить зависимости:
python -m pip install --upgrade pip
pip install -r requirements.txt
3) Создать и применить миграции:
python manage.py makemigrations
python manage.py migrate
4) Запустить проект:
python manage.py runserver
```