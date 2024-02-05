from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication.user import User
from app.utils.exceptions import UserExistError


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    return (await session.scalars(select(User).where(User.username == username))).one_or_none()


async def create_user(session: AsyncSession, user: dict[str, Any]) -> User:
    db_user = User(**user)
    session.add(db_user)

    try:
        await session.commit()
    except IntegrityError:
        raise UserExistError()

    return db_user
