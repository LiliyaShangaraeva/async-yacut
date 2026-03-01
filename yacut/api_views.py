from http import HTTPStatus

from flask import jsonify, request

from yacut import app, db
from yacut.error_handlers import InvalidAPIUsage
from yacut.models import URLMap

REQUIRED_FIELD_ERROR = '\"url\" является обязательным полем!'
EMPTY_BODY_ERROR = 'Отсутствует тело запроса'


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
    url_map = URLMap.create(original, custom_id)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """Получить оригинальный URL по короткому идентификатору."""
    url_map = URLMap.get_or_404(short_id)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
