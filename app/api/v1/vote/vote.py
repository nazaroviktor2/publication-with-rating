from typing import Annotated

from fastapi import Depends, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.vote.router import vote_router
from app.crud.vote import create_or_update_vote, get_vote_by_user_and_publication_id
from app.db.postgres import get_session
from app.models.publication.user import User
from app.schema.vote.vote import Vote, VoteDTO
from app.utils.auth.jwt import get_current_user
from app.utils.exceptions import handle_domain_error


@vote_router.put(
    '', description='Используется для оценки публикации', summary='Update vote', status_code=status.HTTP_200_OK
)
@handle_domain_error
async def create_vote(
    vote: Vote,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    vote = await create_or_update_vote(session, vote.publication_id, current_user.id, vote.value)

    return ORJSONResponse(
        VoteDTO.model_validate(vote, from_attributes=True).model_dump(mode='json'), status_code=status.HTTP_200_OK
    )


@vote_router.delete('', description='Удалят оценку', summary='Delete vote', status_code=status.HTTP_204_NO_CONTENT)
@handle_domain_error
async def delete_vote_by_publication_id(
    publication_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
) -> None:
    db_vote = await get_vote_by_user_and_publication_id(session, publication_id, current_user.id)
    if db_vote:
        await session.delete(db_vote)
        await session.commit()
