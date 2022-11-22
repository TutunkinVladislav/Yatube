import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    dt = datetime.datetime.now()
    return {
        'year': dt.year,
    }
