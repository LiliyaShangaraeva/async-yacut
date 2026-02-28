import random
import string

from yacut.constants import SHORT_ID_LENGTH
from yacut.models import URLMap

ALLOWED_CHARS = string.ascii_letters + string.digits


def get_unique_short_id():
    """Генерирует уникальный короткий идентификатор."""
    while True:
        short_id = ''.join(
            random.choice(ALLOWED_CHARS)
            for _ in range(SHORT_ID_LENGTH)
        )

        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
