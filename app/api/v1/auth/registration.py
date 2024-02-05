from fastapi import Depends, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.router import login_router
from app.crud.user import create_user
from app.db.postgres import get_session
from app.schema.auth.user import UserDTO, UserResponse
from app.utils.exceptions import handle_domain_error


@login_router.post(
    path='/registration',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@handle_domain_error
async def registration(
    payload: UserDTO,
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    new_user = await create_user(session, payload.model_dump())
    return ORJSONResponse(
        UserResponse.model_validate(new_user, from_attributes=True).model_dump(mode='json'),
        status_code=status.HTTP_201_CREATED,
    )
