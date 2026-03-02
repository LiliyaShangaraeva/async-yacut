class URLMapError(Exception):
    """Базовое исключение модели URLMap."""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class ShortIdValidationError(URLMapError):
    """Некорректный short id."""


class ShortIdAlreadyExistsError(URLMapError):
    """Такой short id уже существует."""


class ShortIdGenerationError(URLMapError):
    """Не удалось сгенерировать short id."""


class URLMapNotFoundError(URLMapError):
    """Ссылка не найдена."""
