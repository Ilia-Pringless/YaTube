from datetime import datetime

year_date = int(datetime.now().strftime('%Y'))


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': year_date,
    }
