class APIError(Exception):
    """базовый класс для всех исключений."""
    pass


class UserValueExceptionError(APIError):
    """Имя пользователя не существет в базе."""
    pass
