from app.db.models import async_session, User, ChatSelectionHistory
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


async def get_last_selected(chat_id):
    async with async_session() as session:
        record = await session.get(ChatSelectionHistory, chat_id)
        return record.last_selected if record else []


async def update_last_selected(chat_id, first, second):
    async with async_session() as session:
        record = await session.get(ChatSelectionHistory, chat_id)
        if not record:
            record = ChatSelectionHistory(chat_id=chat_id, last_selected=[])
            session.add(record)
        else:
            record.last_selected = record.last_selected[-2:]

        record.last_selected.append(first)
        record.last_selected.append(second)

        await session.commit()
