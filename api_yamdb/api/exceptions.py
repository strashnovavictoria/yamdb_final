class APIErrors(Exception):
    """базовый класс для всех исключений."""
    pass


class UserValueException(APIErrors):
    """Имя пользователя не существет в базе."""
    pass
