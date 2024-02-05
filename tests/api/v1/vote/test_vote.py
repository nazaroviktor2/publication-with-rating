from pathlib import Path

import pytest
from httpx import AsyncClient
from starlette import status

from tests.const import URLS

from app.crud.vote import get_vote_by_user_and_publication_id

BASE_DIR = Path(__file__).parent

FIXTURES_PATH = BASE_DIR / 'fixtures'


@pytest.mark.parametrize(
    ('username', 'password', 'publication_id', 'fixtures', 'expected_status', 'delete_status'),
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
            status.HTTP_204_NO_CONTENT,
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture_with_redis')
async def test_vote_create_and_delete(
    client: AsyncClient,
    username: str,
    password: str,
    publication_id: int,
    access_token: str,
    expected_status,
    delete_status,
    db_session: None,
) -> None:
    headers = {'Authorization': f'Bearer {access_token}'}
    response = await client.put(
        URLS['api']['v1']['vote']['vote'],
        headers=headers,
        json={'value': -1, 'publication_id': publication_id},
    )
    assert response.status_code == expected_status

    vote = await get_vote_by_user_and_publication_id(db_session, publication_id, 0)

    assert vote is not None
    assert vote.value == -1

    response = await client.delete(
        URLS['api']['v1']['vote']['vote'],
        headers=headers,
        params={'publication_id': publication_id},
    )
    assert response.status_code == delete_status

    vote = await get_vote_by_user_and_publication_id(db_session, publication_id, 0)

    assert vote is None
