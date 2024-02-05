from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, status

USER_ALL_READY_EXIST = 'User all ready exist'
PUBLICATION_NOT_FOUND = 'Publication with id = {id} - not found'
PUBLICATION_FORBIDDEN = 'You do not have permission for this publication'


def handle_domain_error(func: Callable[[Any, Any, Any], Any] | Callable[[Any, Any], Any]) -> Any:
    @wraps(func)
    async def wrapper(*args: tuple[Any], **kwargs: dict[Any, Any]) -> Callable[[Any], Any]:
        try:
            return await func(*args, **kwargs)
        except DomainForbiddenError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))

        except DomainNotFoundError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))

        except DomainError as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return wrapper


class DomainError(Exception):
    pass


class UserExistError(DomainError):
    def __init__(self) -> None:
        super().__init__(USER_ALL_READY_EXIST)


class DomainNotFoundError(DomainError):
    pass


class PublicationNotFoundError(DomainNotFoundError):
    def __init__(self, id: int) -> None:
        super().__init__(PUBLICATION_NOT_FOUND.format(id=id))


class DomainForbiddenError(Exception):
    pass


class PublicationForbiddenError(DomainForbiddenError):
    def __init__(self) -> None:
        super().__init__(PUBLICATION_FORBIDDEN)
