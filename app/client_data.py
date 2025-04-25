import os
import asyncio
from pyrogram import Client, utils
import app.db.requests as rq


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
    api_id = os.getenv("ID")
    api_hash = os.getenv("HASH")
    bot_token = os.getenv("TOKEN")

    app = Client(
        name="bot",
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        in_memory=True
    )

    try:
        print("Старт pyrogram")
        await asyncio.wait_for(app.start(), timeout=25)
        print("Клиент запущен")

        chat = await app.get_chat(chat_id)
        print(f"Чат найден: {chat.title}")

        print("Получаю участников:")
        async for member in app.get_chat_members(chat_id):
            username = member.user.username
            if username and username != "ReviewerPickerBot":
                print(f"Добавляю пользователя: {username}")
                await rq.set_user(username, chat_id)
            await asyncio.sleep(1)

    except asyncio.TimeoutError:
        print("Таймаут при подключении клиента.")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if app.is_connected:
            await app.stop()
            print("Клиент остановлен.")
