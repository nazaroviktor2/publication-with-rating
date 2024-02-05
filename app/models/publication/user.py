from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.meta import Base
from app.models.publication.publication import Publication


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String, unique=True)

    password: Mapped[str] = mapped_column(String)

    publications: Mapped[list[Publication]] = relationship('Publication', backref='author', lazy='selectin')
