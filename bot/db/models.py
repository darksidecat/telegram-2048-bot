from sqlalchemy import BigInteger, Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class GameHistoryEntry(Base):
    __tablename__ = "gameshistory"

    game_id = Column(UUID(as_uuid=True), primary_key=True)
    played_at = Column(DateTime, nullable=False)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    field_size = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
