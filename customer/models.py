from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, BigInteger
from database import Base

class User(Base):

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    crm_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    tg_name: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    chat_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
