import re
from http import HTTPStatus

from flask import jsonify, request
from yacut import app, db
from yacut.constants import MAX_SHORT_ID_LENGTH, MIN_SHORT_ID_LENGTH
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap
from yacut.utils import get_unique_short_id

REQUIRED_FIELD_ERROR = '\"url\" является обязательным полем!'
EMPTY_BODY_ERROR = 'Отсутствует тело запроса'
SHORT_ID_EXISTS_ERROR = 'Предложенный вариант короткой ссылки уже существует.'
INVALID_SHORT_ID_LENGTH = 'Указано недопустимое имя для короткой ссылки'
ID_NOT_FOUND_ERROR = 'Указанный id не найден'


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """Создать короткую ссылку по API."""
    data = request.get_json(silent=True)

    if not data:
        raise InvalidAPIUsage(EMPTY_BODY_ERROR)

    if 'url' not in data:
        raise InvalidAPIUsage(REQUIRED_FIELD_ERROR)

    original = data.get('url')
    custom_id = data.get('custom_id') or None

    if custom_id is not None:

        if not (MIN_SHORT_ID_LENGTH <= len(custom_id) <= MAX_SHORT_ID_LENGTH):
            raise InvalidAPIUsage(INVALID_SHORT_ID_LENGTH)

        if not re.match(r'^[A-Za-z0-9]+$', custom_id):
            raise InvalidAPIUsage(INVALID_SHORT_ID_LENGTH)

        if (
            custom_id == 'files'
            or URLMap.query.filter_by(short=custom_id).first()
        ):
            raise InvalidAPIUsage(SHORT_ID_EXISTS_ERROR)

        short = custom_id
    else:
        short = get_unique_short_id()

    url_map = URLMap(
        original=original,
        short=short
    )

    db.session.add(url_map)
    db.session.commit()

    return jsonify(
        {
            'url': url_map.original,
            'short_link': request.host_url + url_map.short
        }
    ), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получить оригинальный URL по короткому идентификатору."""
    url_map = URLMap.query.filter_by(short=short_id).first()

    if url_map is None:
        raise InvalidAPIUsage(ID_NOT_FOUND_ERROR, HTTPStatus.NOT_FOUND)

    return jsonify({'url': url_map.original}), HTTPStatus.OK
