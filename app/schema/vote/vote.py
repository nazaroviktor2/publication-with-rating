from pydantic import BaseModel, field_validator

from app.schema.crud import IdField


class VoteValue(BaseModel):
    value: int = 1

    @field_validator('value')
    @classmethod
    def validate_value(cls, value: int) -> int:
        if value not in (-1, 1):
            raise ValueError("Values must be equals '-1' for dislike or '1' for like")
        return value


class Vote(VoteValue):
    publication_id: int


class VoteDTO(IdField, Vote):
    pass
