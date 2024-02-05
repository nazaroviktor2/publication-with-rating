from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.publication.publication import Publication
from app.models.publication.vote import Vote
from app.utils.exceptions import PublicationForbiddenError, PublicationNotFoundError


async def get_publication_by_id(session: AsyncSession, publication_id: int) -> Publication:
    db_publication = await session.get(Publication, publication_id)
    if not db_publication:
        raise PublicationNotFoundError(publication_id)

    return db_publication


async def create_new_publication(session: AsyncSession, text: str, author_id: int) -> Publication:
    db_publication = Publication(text=text, author_id=author_id)
    session.add(db_publication)
    await session.commit()

    return db_publication


async def get_publications(session: AsyncSession, skip: int, limit: int) -> Sequence[Publication]:
    res = await session.scalars(
        select(Publication, Publication.votes)
        .join(Vote, isouter=True)
        .order_by(func.sum(Vote.value).desc().nullslast())
        .group_by(Publication, Vote.publication_id)
        .options(selectinload(Publication.votes))
        .offset(skip)
        .limit(limit)
    )

    return res.all()


async def update_or_create_publication(
    session: AsyncSession, publication_id: int, text: str, author_id: int
) -> Publication:
    publication: Publication | None = await session.get(Publication, publication_id)

    if not publication:
        return await create_new_publication(session, text, author_id)

    if publication.author_id != author_id:
        raise PublicationForbiddenError()

    publication.text = text

    session.add(publication)
    await session.commit()
    return publication
