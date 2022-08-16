from django.core.exceptions import ValidationError


def username_validation(username):
    if username == 'me':
        raise ValidationError("Нельзя использовать имя 'me'")
