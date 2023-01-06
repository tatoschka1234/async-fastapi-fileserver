from pathlib import Path
from httpx import AsyncClient
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import app

test_user1 = "test_user1"
test_user1_psw = "psw"

test_file_name = 'for_tests_1.txt'
test_downloads_folder_name = 'for_tests_download'


async def test_get_file_list_403(client: AsyncClient,
                          async_session: AsyncSession) -> None:
    response = await client.get(app.url_path_for("get_files"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_download_file_403(client: AsyncClient,
                          async_session: AsyncSession) -> None:
    response = await client.get(app.url_path_for("get_file"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_upload_file_403(client: AsyncClient,
                          async_session: AsyncSession) -> None:
    response = await client.post(app.url_path_for("upload_file"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_search_file_403(client: AsyncClient,
                          async_session: AsyncSession) -> None:
    response = await client.get(app.url_path_for("files_search"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_register(client: AsyncClient,
                          async_session: AsyncSession) -> None:
    response = await client.post(app.url_path_for("user_register"), json={
                'username': test_user1,
                'password': test_user1_psw
            })
    assert response.status_code == HTTPStatus.CREATED


async def test_auth(client: AsyncClient,
                          async_session: AsyncSession) -> None:
    response = await client.post(app.url_path_for("user_auth"),
                                 data={
                                     'username': test_user1,
                                     'password': test_user1_psw,
                                 }
                                 )
    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.json()


async def test_get_file_empty_list(client_authorized: AsyncClient,

                          async_session: AsyncSession) -> None:
    response = await client_authorized.get(app.url_path_for("get_files"))
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


async def test_upload_file(client_authorized: AsyncClient,
                          async_session: AsyncSession) -> None:
    path_folder = Path(test_downloads_folder_name).resolve()
    path_file = Path(test_file_name)
    file = {'file': path_file.open('rb')}
    response = await client_authorized.post(app.url_path_for("upload_file"),
                                            params={
                                                'path': str(path_folder) + '/',
                                            },
                                            files=file,
                                            )
    assert response.status_code == HTTPStatus.OK


async def test_get_file_list(client_authorized: AsyncClient,
                          async_session: AsyncSession) -> None:
    response = await client_authorized.get(app.url_path_for("get_files"))
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    res = response.json()[0]
    assert res['name'] == test_file_name


async def test_download_file_by_path(client_authorized: AsyncClient,
                          async_session: AsyncSession) -> None:
    path = Path(test_downloads_folder_name, test_file_name).resolve()
    response = await client_authorized.get(app.url_path_for("get_file"),
                                           params={
                                               'file_id': str(path)
                                           },
                                           )
    assert response.status_code == HTTPStatus.OK
    content = None
    with open(test_file_name) as f:
        content = f.read()
    assert content
    assert response.text == content


async def test_file_search(client_authorized: AsyncClient,
                          async_session: AsyncSession) -> None:
    response = await client_authorized.get(app.url_path_for("files_search"),
                params={'extension': "txt"})
    assert response.status_code == HTTPStatus.OK
    res = response.json()
    assert len(res['matches']) == 1
    assert res['matches'][0]['name'] == test_file_name


async def test_ping(client: AsyncClient,
                          async_session: AsyncSession) -> None:
    response = await client.get(app.url_path_for("get_health"))
    assert response.status_code == HTTPStatus.OK
    res = response.json()
    assert 'db' in res
    assert 'cache' in res
    assert res['db'] > 0
    assert res['cache'] > 0
