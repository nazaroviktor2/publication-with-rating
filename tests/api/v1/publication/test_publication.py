from pathlib import Path

import pytest
from httpx import AsyncClient
from starlette import status

from tests.const import URLS

from app.crud.vote import get_vote_by_user_and_publication_id
from app.models.publication.publication import Publication

BASE_DIR = Path(__file__).parent

FIXTURES_PATH = BASE_DIR / 'fixtures'


@pytest.mark.parametrize(
    ('username', 'password', 'fixtures', 'expected_status'),
    [
        (
            'test_client',
            'secret',
            [
                FIXTURES_PATH / 'publication.user.json',
                FIXTURES_PATH / 'publication.publication.json',
            ],
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_get_publication(
    client: AsyncClient,
    username: str,
    password: str,
    access_token: str,
    expected_status,
    db_session: None,
) -> None:
    headers = {'Authorization': f'Bearer {access_token}'}

    response = await client.get(URLS['api']['v1']['publication']['publication'], headers=headers)
    assert response.status_code == expected_status
    assert len(response.json()) >= 1


@pytest.mark.parametrize(
    ('username', 'password', 'fixtures', 'expected_status'),
    [
        (
            'test_client',
            'secret',
            [

            ],
            status.HTTP_404_NOT_FOUND,
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_get_wrong_publication(
    client: AsyncClient,
    username: str,
    password: str,
    access_token: str,
    expected_status,
    db_session: None,
) -> None:
    response = await client.get(URLS['api']['v1']['publication']['publication'] + "/2132131")
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    (
        'username',
        'password',
        'text',
        'fixtures',
        'expected_status',
        'get_status',
    ),
    [
        (
            'test_client',
            'secret',
            'some text',
            [
                FIXTURES_PATH / 'publication.user.json',
            ],
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture_with_redis')
async def test_create_publication_and_get(
    client: AsyncClient,
    username: str,
    password: str,
    text: str,
    access_token: str,
    expected_status,
    get_status,
    db_session: None,
) -> None:
    headers = {'Authorization': f'Bearer {access_token}'}

    response = await client.post(
        URLS['api']['v1']['publication']['publication'],
        headers=headers,
        json={'text': text},
    )
    assert response.status_code == expected_status
    assert response.json().get('text') == text
    publication_id = response.json().get('id')

    new_publication_db = await db_session.get(Publication, publication_id)

    assert new_publication_db.text == text

    response = await client.get(URLS['api']['v1']['publication']['publication'] + '/' + str(publication_id))
    assert response.status_code == get_status

    assert response.json()['text'] == text


@pytest.mark.parametrize(
    (
        'username',
        'password',
        'text',
        'new_text',
        'fixtures',
        'expected_status',
    ),
    [
        (
            'test_client',
            'secret',
            'some text',
            'new_text',
            [
                FIXTURES_PATH / 'publication.user.json',
            ],
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture_with_redis')
async def test_update_publication(
    client: AsyncClient,
    username: str,
    password: str,
    text: str,
    new_text: str,
    access_token: str,
    expected_status,
    db_session: None,
) -> None:
    headers = {'Authorization': f'Bearer {access_token}'}

    response = await client.post(
        URLS['api']['v1']['publication']['publication'],
        headers=headers,
        json={'text': text},
    )
    publication_id = response.json().get('id')

    response = await client.put(
        URLS['api']['v1']['publication']['publication'] + '/' + str(publication_id),
        headers=headers,
        json={'text': new_text},
    )

    assert response.status_code == expected_status
    assert response.json().get('text') == new_text

    publication_db = await db_session.get(Publication, publication_id)

    assert publication_db.text == new_text


@pytest.mark.parametrize(
    ('username', 'password', 'publication_id', 'fixtures', 'expected_status'),
    [
        (
            'test_client',
            'secret',
            0,
            [
                FIXTURES_PATH / 'publication.user.json',
                FIXTURES_PATH / 'publication.publication.json',
            ],
            status.HTTP_204_NO_CONTENT,
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture_with_redis')
async def test_delete_publication(
    client: AsyncClient,
    username: str,
    password: str,
    publication_id: int,
    access_token: str,
    expected_status,
    db_session: None,
) -> None:
    headers = {'Authorization': f'Bearer {  access_token}'}
    old_event = await db_session.get(Publication, publication_id)
    assert old_event is not None
    response = await client.delete(
        URLS['api']['v1']['publication']['publication'] + '/' + str(publication_id),
        headers=headers,
    )
    assert response.status_code == expected_status
    old_event = await db_session.get(Publication, publication_id)

    assert old_event is None


@pytest.mark.parametrize(
    ('username', 'password', 'publication_id', 'fixtures', 'expected_status'),
    [
        (
            'test_client',
            'secret',
            0,
            [
                FIXTURES_PATH / 'publication.user.json',
                FIXTURES_PATH / 'publication.publication.json',
            ],
            status.HTTP_200_OK,
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture_with_redis')
async def test_publication_vote(
    client: AsyncClient,
    username: str,
    password: str,
    publication_id: int,
    access_token: str,
    expected_status,
    db_session: None,
) -> None:
    headers = {'Authorization': f'Bearer {access_token}'}
    response = await client.put(
        URLS['api']['v1']['publication']['vote'].format(publication_id=publication_id),
        headers=headers,
        json={'value': -1},
    )
    assert response.status_code == expected_status

    vote = await get_vote_by_user_and_publication_id(db_session, publication_id, 0)

    assert vote is not None
    assert vote.value == -1
