from pyrogram import Client, utils
import app.db.requests as rq
import asyncio
from config import api_id, api_hash, bot_token


def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"


utils.get_peer_type = get_peer_type_new


async def get_chat_members(chat_id):
    app = Client("Имя | Бот", api_id=api_id, api_hash=api_hash, bot_token=bot_token, in_memory=True)
    try:
        await app.start()
        try:
            chat = await app.get_chat(chat_id)
            print(f"Чат найден: {chat.title}")
        except Exception as e:
            print(f"Чат с ID {chat_id} не найден или бот не имеет доступа: {e}")
            return

        async for member in app.get_chat_members(chat_id):
            print(member.user.username)
            if member.user.username != "ReviewerPickerBot" and member.user.username:
                await rq.set_user(member.user.username)
            await asyncio.sleep(1)
    except ValueError as e:
        print(f"Ошибка при получении участников чата: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if app.is_connected:
            await app.stop()
    return
