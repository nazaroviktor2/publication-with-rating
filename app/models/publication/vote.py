from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.meta import Base


class Vote(Base):
    __tablename__ = 'votes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    publication_id: Mapped[int] = mapped_column(Integer, ForeignKey('publication.id'))
