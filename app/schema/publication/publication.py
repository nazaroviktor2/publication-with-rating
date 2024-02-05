from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.schema.crud import IdField
from app.schema.vote.vote import Vote, VoteValue


class Publication(BaseModel):
    text: str = Field(description='Текст публикации', examples=['Текст публикации'])


class NewPublication(Publication, IdField):
    author_id: int = Field(description='Уникальный индефикатор автора', examples=[1])
    publication_date: datetime = Field(description='Дата публикации')


class PublicationDTO(NewPublication, IdField):
    votes: list[Vote] = Field(description='Список оценок публикации')
    rating: int | None = Field(None, description='Рейтинг публикации (положительные - отрицательные оценки)')

    @model_validator(mode='after')
    def calculate_rating(self) -> Self:
        if not self.rating:
            self.rating = sum([vote.value for vote in self.votes])

        return self


class VoteForPublication(VoteValue):
    pass
