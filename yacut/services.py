import urllib

import aiohttp
from flask import current_app

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


async def upload_files_to_disk(files):
    """Загружает список файлов и возвращает ссылки для скачивания."""
    token = current_app.config['DISK_TOKEN']
    headers = {
        'Authorization': f'OAuth {token}'
    }

    results = []

    async with aiohttp.ClientSession(headers=headers) as session:
        for file in files:
            disk_path = f'app:/{file.filename}'
            params = {
                'path': disk_path,
                'overwrite': 'true'
            }

            async with session.get(
                UPLOAD_URL,
                params=params
            ) as response:
                data = await response.json()
                upload_url = data.get('href')

            file.stream.seek(0)

            async with session.put(
                upload_url,
                data=file.stream
            ) as response:
                location = response.headers.get('Location')
                if location:
                    location = urllib.parse.unquote(location)
                await response.read()

            async with session.get(
                DOWNLOAD_URL,
                params={'path': disk_path}
            ) as response:
                data = await response.json()
                download_link = data.get('href')
                if download_link:
                    download_link = urllib.parse.unquote(download_link)

            results.append({
                'filename': file.filename,
                'disk_path': disk_path
            })

    return results
