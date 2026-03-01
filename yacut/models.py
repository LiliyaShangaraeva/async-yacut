import random
import re
from datetime import datetime
from http import HTTPStatus

from flask import url_for

from yacut import db
from yacut.constants import (ALLOWED_CHARS, CUSTOM_ID_PATTERN,
                             FORBIDDEN_SHORT_IDS,
                             MAX_ATTEMPTS_TO_GENERATE_SHORT_ID,
                             MAX_SHORT_ID_LENGTH, MIN_SHORT_ID_LENGTH,
                             SHORT_ID_LENGTH)
from yacut.error_handlers import InvalidAPIUsage

SHORT_ID_EXISTS_ERROR = 'Предложенный вариант короткой ссылки уже существует.'
INVALID_SHORT_ID_LENGTH = 'Указано недопустимое имя для короткой ссылки'
ID_NOT_FOUND_ERROR = 'Указанный id не найден'


class URLMap(db.Model):
    """Модель для хранения соответствия короткой ссылки и оригинального URL."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(), nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_ID_LENGTH),
        nullable=False,
        unique=True,
        index=True
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def create(original, custom_id=None):
        """Создаёт новую запись URLMap."""
        if custom_id is not None:

            if not (
                MIN_SHORT_ID_LENGTH <= len(custom_id) <= MAX_SHORT_ID_LENGTH
            ):
                raise InvalidAPIUsage(INVALID_SHORT_ID_LENGTH)

            if not re.match(CUSTOM_ID_PATTERN, custom_id):
                raise InvalidAPIUsage(INVALID_SHORT_ID_LENGTH)

            if (
                custom_id in FORBIDDEN_SHORT_IDS
                or URLMap.query.filter_by(short=custom_id).first()
            ):
                raise InvalidAPIUsage(SHORT_ID_EXISTS_ERROR)

            short = custom_id
        else:
            short = URLMap.generate_unique_short_id()

        url_map = URLMap(original=original, short=short)

        db.session.add(url_map)
        return url_map

    def to_dict(self):
        """Возвращает словарь для JSON-ответа API."""
        return {
            'url': self.original,
            'short_link': url_for(
                'redirect_view', short_id=self.short, _external=True
            )
        }

    @staticmethod
    def get_or_404(short_id):
        """Возвращает URLMap по short_id или вызывает InvalidAPIUsage(404)."""
        url_map = URLMap.query.filter_by(short=short_id).first()
        if url_map is None:
            raise InvalidAPIUsage(ID_NOT_FOUND_ERROR, HTTPStatus.NOT_FOUND)
        return url_map

    def public_short_link(self):
        """Возвращает полный публичный URL короткой ссылки."""
        return url_for('redirect_view', short_id=self.short, _external=True)

    @staticmethod
    def is_short_id_available(short_id):
        """Возвращает True, если short_id свободен."""
        return URLMap.query.filter_by(short=short_id).first() is None

    @staticmethod
    def generate_unique_short_id():
        """Генерирует уникальный short_id."""
        for _ in range(MAX_ATTEMPTS_TO_GENERATE_SHORT_ID):
            short_id = ''.join(
                random.choice(ALLOWED_CHARS)
                for _ in range(SHORT_ID_LENGTH)
            )

            if URLMap.is_short_id_available(short_id):
                return short_id
        raise InvalidAPIUsage(
            "Не удалось сгенерировать уникальный ID",
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
