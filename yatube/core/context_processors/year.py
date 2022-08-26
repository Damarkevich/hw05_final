from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    year = timezone.now().year
    return {
        'year': year,
        # поставил {% now 'Y' %} в шаблон футера,
        # но эту функцию убрать не могу, т.к.
        # без нее проект не проходит тесты.
    }
