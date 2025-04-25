from sqlalchemy import DateTime, String, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///db.sqlite3")
engine = create_async_engine(url=db_url)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(primary_key=True)
    available: Mapped[bool] = mapped_column()
    date_to_available: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class ChatSelectionHistory(Base):
    __tablename__ = "chat_selection_history"

    chat_id: Mapped[str] = mapped_column(String, primary_key=True)
    last_selected: Mapped[list[str]] = mapped_column(JSON, default=[])


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Table created")
