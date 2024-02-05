from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.publication.router import publication_router
from app.cache.cache import redis_drop_key, redis_get, redis_set
from app.crud.publication import (
    create_new_publication,
    get_publication_by_id,
    get_publications,
    update_or_create_publication,
)
from app.crud.vote import create_or_update_vote
from app.db.postgres import get_session
from app.models.publication.user import User
from app.schema.publication.publication import NewPublication, Publication, PublicationDTO, VoteForPublication
from app.utils.auth.jwt import get_current_user
from app.utils.exceptions import handle_domain_error


@publication_router.get(
    '',
    description='Возвращает `limit` лучших публикаций начиная со `skip`',
    summary='Top publications',
    status_code=status.HTTP_200_OK,
)
@handle_domain_error
async def get_top_publications(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 10,
) -> ORJSONResponse:
    publications = await get_publications(session, skip, limit)

    return ORJSONResponse(
        [
            PublicationDTO.model_validate(publication, from_attributes=True).model_dump(mode='json')
            for publication in publications
        ]
    )


@publication_router.post(
    '', description='Создает новую публикацию', summary='New publication', status_code=status.HTTP_201_CREATED
)
@handle_domain_error
async def create_publication(
    publication: Publication,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    new_publication = await create_new_publication(session, publication.text, current_user.id)

    return ORJSONResponse(
        NewPublication.model_validate(new_publication, from_attributes=True).model_dump(mode='json'),
        status_code=status.HTTP_201_CREATED,
    )


@publication_router.get(
    '/{publication_id}', description='Возвращает публикацию', summary='Get publication', status_code=status.HTTP_200_OK
)
@handle_domain_error
async def get_publication(
    publication_id: int,
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    cached_publication = await redis_get(Publication.__name__, publication_id)
    if cached_publication:
        return ORJSONResponse(cached_publication)

    serialized_publication = PublicationDTO.model_validate(
        await get_publication_by_id(session, publication_id), from_attributes=True
    ).model_dump(mode='json')
    await redis_set(Publication.__name__, publication_id, serialized_publication)

    return ORJSONResponse(serialized_publication)


@publication_router.put(
    '/{publication_id}',
    description='Обновляет публикацию',
    summary='Update publication',
    status_code=status.HTTP_200_OK,
)
@handle_domain_error
async def update_publication(
    publication_id: int,
    publication: Publication,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    db_publication = await update_or_create_publication(session, publication_id, publication.text, current_user.id)
    await redis_drop_key(Publication.__name__, publication_id)

    return ORJSONResponse(
        NewPublication.model_validate(db_publication, from_attributes=True).model_dump(mode='json'),
    )


@publication_router.put(
    '/{publication_id}/vote',
    description='Используется для оценки публикации',
    summary='Update vote',
    status_code=status.HTTP_200_OK,
)
@handle_domain_error
async def update_publication_vote(
    publication_id: int,
    vote: VoteForPublication,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
) -> str:
    await create_or_update_vote(session, publication_id, current_user.id, vote.value)
    await redis_drop_key(Publication.__name__, publication_id)

    return 'ok'


@publication_router.delete(
    '/{publication_id}',
    description='Удаляет публикацию',
    summary='Delete publication',
    status_code=status.HTTP_204_NO_CONTENT,
)
@handle_domain_error
async def delete_publication(
    publication_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
) -> None:
    publication = await get_publication_by_id(session, publication_id)
    if publication.author_id != current_user.id:
        raise HTTPException(detail='Permission denied', status_code=status.HTTP_403_FORBIDDEN)
    await session.delete(publication)
    await session.commit()
    await redis_drop_key(Publication.__name__, publication_id)
