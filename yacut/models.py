from datetime import datetime

from yacut import db
from yacut.constants import MAX_SHORT_ID_LENGTH


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
