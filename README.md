# 📓 Блог с базой данных

Учебное приложение-блог, демонстрирующее работу с базой данных SQLite через **Flask-SQLAlchemy** и миграции с помощью **Flask-Migrate**.

## 🗄️ Функциональность
- Главная страница с таблицей успеваемости (добавлена 4-я тема — SQL).
- Страница «Дневник программиста» с формой добавления записей.
- Записи сохраняются в базу данных SQLite (таблица `notes`).
- Вывод всех записей из БД на страницу.
- Модель `Notes` содержит поля: `id`, `title`, `subtitle`, `text`.
- Выполнены две миграции:初始 creation и добавление колонки `subtitle`.

## 🛠️ Технологии
- Python 3, Flask
- Flask-SQLAlchemy (ORM)
- Flask-Migrate (Alembic)
- SQLite
- HTML5, CSS3, Jinja2

## 🚀 Запуск

pip install flask flask-sqlalchemy flask-migrate

flask db upgrade   # применить миграции

python app.py

📂 Структура

app.py — настройка БД, модель Notes, маршруты.

migrations/ — скрипты миграций.

instance/notes.db — файл базы данных SQLite.

templates/ — HTML-шаблоны.

static/style.css — стили.