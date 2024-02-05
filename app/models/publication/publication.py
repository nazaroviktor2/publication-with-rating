from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.meta import Base
from app.models.publication.vote import Vote


class Publication(Base):
    __tablename__ = 'publication'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String)
    publication_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))

    votes: Mapped[Vote] = relationship('Vote', backref='publication', lazy='selectin')
