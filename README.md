# hw05_final

Cоциальная сеть на которой пользователи имеют возможность создать учетную запись, публиковать записи, подписываться на авторов и комментировать их записи. Также можно создать свою страницу, если на нее зайти, то можно посмотреть все записи автора. Проект покрыт тестами при помощи стандартной библиотеки Python UnitTest.

## Стек:
- Python 3.7
- Django 3.2.16
- UnitTest

---
## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/TutunkinVladislav/hw05_final.git
```

Cоздать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python3 manage.py migrate
```

Запустить проект:

```bash
python3 manage.py runserver
```
