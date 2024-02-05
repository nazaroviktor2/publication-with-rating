from pydantic import BaseModel, Field, field_validator

from app.schema.crud import IdField
from app.utils.auth.password import hash_password


class UserResponse(IdField):
    username: str = Field(description='Имя пользователя')


class UserDTO(BaseModel):
    username: str = Field(description='Имя пользователя')
    password: str = Field(description='Пароль')

    @field_validator('password')
    @classmethod
    def hash_password(cls, v: str) -> str:
        return hash_password(v)
