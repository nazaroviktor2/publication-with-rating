from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.publication import get_publication_by_id
from app.models.publication.vote import Vote
from app.utils.exceptions import PublicationNotFoundError


async def create_or_update_vote(session: AsyncSession, publication_id: int, user_id: int, value: int) -> Vote:
    res = await session.scalars(
        select(Vote).where(Vote.publication_id == publication_id).where(Vote.user_id == user_id),
    )
    db_vote = res.one_or_none()
    if not db_vote:
        db_publication = await get_publication_by_id(session, publication_id)
        if not db_publication:
            raise PublicationNotFoundError(id=publication_id)

        db_vote = Vote(publication_id=publication_id, user_id=user_id, value=value)

    db_vote.value = value
    session.add(db_vote)
    await session.commit()

    return db_vote


async def get_vote_by_user_and_publication_id(session: AsyncSession, publication_id: int, user_id: int) -> Vote | None:
    db_vote = await session.scalars(
        select(Vote).where(Vote.publication_id == publication_id).where(Vote.user_id == user_id),
    )

    return db_vote.one_or_none()
