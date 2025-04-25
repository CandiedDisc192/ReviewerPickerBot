from app.db.models import async_session
from app.db.models import User
from sqlalchemy import select, update


async def set_user(username, chat_id):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.username == username).where(User.chat_id == chat_id)
        )

        if not user:
            session.add(User(username=username, chat_id=chat_id, available=True))
            await session.commit()


async def set_user_available(username, chat_id, available, date_to_available=None):
    async with async_session() as session:
        stmt = (
            update(User).where(User.username == username).where(User.chat_id == chat_id)
        )
        if available is not None:
            stmt = stmt.values(available=available)
        if date_to_available is not None:
            stmt = stmt.values(date_to_available=date_to_available)
        await session.execute(stmt)
        await session.commit()


async def get_active_users(chat_id):
    async with async_session() as session:
        stmt = (
            select(User.username).where(User.available).where(User.chat_id == chat_id)
        )
        result = await session.scalars(stmt)
        return [user for user in result]
