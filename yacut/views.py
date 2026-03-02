import urllib
from http import HTTPStatus

import requests
from flask import abort, current_app, flash, redirect, render_template

from yacut import app, db
from yacut.exceptions import URLMapError, ShortIdGenerationError
from yacut.forms import UploadForm, URLMapForm
from yacut.models import URLMap
from yacut.services import DOWNLOAD_URL, upload_files_to_disk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница сервиса сокращения ссылок."""
    form = URLMapForm()

    if form.validate_on_submit():
        custom_id = form.custom_id.data
        original = form.original_link.data

        try:
            url_map = URLMap.create(original, custom_id)
        except URLMapError as e:
            flash(e.message)
            return render_template('index.html', form=form)

        return render_template(
            'index.html',
            form=form,
            short_url=url_map.short,
            public_short_link=url_map.public_short_link()
        )

    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
async def upload_files():
    """Страница загрузки файлов и создания коротких ссылок на них."""
    form = UploadForm()

    if form.validate_on_submit():
        files = form.files.data

        uploaded_files = await upload_files_to_disk(files)
        result = []
        try:
            for item in uploaded_files:
                short = URLMap.generate_unique_short_id()

                url_map = URLMap(
                    original=item['disk_path'],
                    short=short
                )
                db.session.add(url_map)

                result.append({
                    'filename': item['filename'],
                    'short': short,
                    'public_short_link': url_map.public_short_link()
                })

            db.session.commit()
        except ShortIdGenerationError as e:
            db.session.rollback()
            flash(f"Ошибка при создании ссылки: {e.message}")
            return render_template('upload.html', form=form)

        return render_template(
            'upload.html',
            form=form,
            result=result
        )

    return render_template('upload.html', form=form)


@app.route('/<string:short_id>')
def redirect_view(short_id):
    """Перенаправляет по короткому идентификатору на оригинальный URL."""
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()

    if not url_map.original.startswith('app:/'):
        return redirect(url_map.original)

    token = current_app.config['DISK_TOKEN']
    headers = {
        'Authorization': f'OAuth {token}'
    }

    response = requests.get(
        DOWNLOAD_URL,
        headers=headers,
        params={'path': url_map.original}
    )

    data = response.json()
    download_link = data.get('href')

    if not download_link:
        abort(HTTPStatus.NOT_FOUND)

    download_link = urllib.parse.unquote(download_link)

    return redirect(download_link)
