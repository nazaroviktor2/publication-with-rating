from datetime import timedelta
from typing import Annotated

from fastapi import Depends, status
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.router import login_router
from app.db.postgres import get_session
from app.models.publication.user import User
from app.schema.auth.token import Token
from app.schema.auth.user import UserResponse
from app.utils.auth.jwt import authenticate_user, create_access_token, get_current_user, oauth2_scheme
from conf.config import settings


@login_router.get('/users/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    return ORJSONResponse(UserResponse.model_validate(current_user, from_attributes=True).model_dump(mode='json'))


@login_router.post('/info')
async def info(
    access_token: Annotated[str, Depends(oauth2_scheme)],
) -> ORJSONResponse:
    return ORJSONResponse(access_token)


@login_router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type='bearer')
