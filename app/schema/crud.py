from pydantic import BaseModel, Field


class IdField(BaseModel):
    id: int = Field(description='Уникальный идентификатор объекта')
