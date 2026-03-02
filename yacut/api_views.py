from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from yacut.error_handlers import InvalidAPIUsage
from yacut.exceptions import URLMapError, URLMapNotFoundError
from yacut.models import URLMap

REQUIRED_FIELD_ERROR = '\"url\" является обязательным полем!'
EMPTY_BODY_ERROR = 'Отсутствует тело запроса'
INTERNAL_SERVER_ERROR = 'Внутренняя ошибка сервера'


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
    try:
        url_map = URLMap.create(original, custom_id)
    except URLMapError as e:
        raise InvalidAPIUsage(e.message, HTTPStatus.BAD_REQUEST)
    except Exception:
        raise InvalidAPIUsage(
            INTERNAL_SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получить оригинальный URL по короткому идентификатору."""
    try:
        url_map = URLMap.get_or_404(short_id)
    except URLMapNotFoundError as e:
        raise InvalidAPIUsage(e.message, HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
