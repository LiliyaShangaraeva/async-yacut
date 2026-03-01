from http import HTTPStatus

from flask import jsonify, render_template, request

from yacut import app, db


class InvalidAPIUsage(Exception):
    """Исключение для ошибок API."""

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {'message': self.message}


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    """Обработчик ошибки 404 для пользовательского интерфейса и API."""
    if request.path.startswith('/api/'):
        return (
            jsonify({'message': 'Указанный id не найден'}),
            HTTPStatus.NOT_FOUND
        )
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    """Обработчик ошибки 500."""
    db.session.rollback()
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
