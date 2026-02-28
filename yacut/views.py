import urllib
from http import HTTPStatus

import requests
from flask import abort, current_app, flash, redirect, render_template
from yacut import app, db
from yacut.forms import UploadForm, URLMapForm
from yacut.models import URLMap
from yacut.services import DOWNLOAD_URL, upload_files_to_disk
from yacut.utils import get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница сервиса сокращения ссылок."""
    form = URLMapForm()

    if form.validate_on_submit():
        custom_id = form.custom_id.data
        original = form.original_link.data

        if not custom_id:
            short = get_unique_short_id()
        elif (
            custom_id == 'files'
            or URLMap.query.filter_by(short=custom_id).first()
        ):
            flash('Предложенный вариант короткой ссылки уже существует.')
            return render_template('index.html', form=form)
        else:
            short = custom_id

        url_map = URLMap(
            original=original,
            short=short
        )
        db.session.add(url_map)
        db.session.commit()

        return render_template(
            'index.html',
            form=form,
            short_url=short
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

        for item in uploaded_files:
            short = get_unique_short_id()

            url_map = URLMap(
                original=item['disk_path'],
                short=short
            )
            db.session.add(url_map)

            result.append({
                'filename': item['filename'],
                'short': short
            })

        db.session.commit()

        return render_template(
            'upload.html',
            form=form,
            result=result
        )

    return render_template('upload.html', form=form)


@app.route('/<string:short_id>')
def redirect_view(short_id):
    """Перенаправляет по короткому идентификатору на оригинальный URL."""
    url_map = URLMap.query.filter_by(short=short_id).first()

    if url_map is None:
        abort(HTTPStatus.NOT_FOUND)

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
