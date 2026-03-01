from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from yacut.constants import (CUSTOM_ID_PATTERN, MAX_SHORT_ID_LENGTH,
                             MIN_SHORT_ID_LENGTH)


class URLMapForm(FlaskForm):
    """Форма создания короткой ссылки на главной странице."""

    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(MIN_SHORT_ID_LENGTH, MAX_SHORT_ID_LENGTH),
            Optional(),
            Regexp(
                CUSTOM_ID_PATTERN,
                message='Используйте только латинские буквы и цифры.'
            )
        ]
    )


class UploadForm(FlaskForm):
    """Форма загрузки нескольких файлов на страницу /files."""

    files = MultipleFileField(
        'Файлы',
        validators=[
            DataRequired(message='Нужно выбрать хотя бы один файл')
        ]
    )
