import re
import random
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from collections import deque
import app.keyboards as kb
from app.client_data import get_chat_members
import app.db.requests as rq
from app.texts import info_message, command_list, pool_message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.chat.type != "private":
        await message.reply(
            "<b>Привет!</b> Я помогу назначить двух случайных участников этого чата на проверку MR.",
            reply_markup=kb.catalog,
            parse_mode="HTML",
        )
        await message.reply("Подождите, собираю информацию об участниках чата...")
        await get_chat_members(message.chat.id)
        await message.reply("Бот готов к работе")
    else:
        await message.reply(
            "<b>Привет!</b>\nЯ помогу назначить двух случайных участников чата на проверку MR.\nПросто добавьте меня "
            "в ваш рабочий чат и напишите команду /start.",
            reply_markup=kb.catalog,
            parse_mode="HTML",
        )


@router.message(Command("unavailable"))
async def cmd_unavailable(message: Message):
    if message.chat.type != "private":
        user = message.from_user
        username = user.username
        await rq.set_user_available(username, message.chat.id, False)
        await message.answer(
            "Вы больше не в списке ревьюверов. Чтобы вернуться в него, вызовите команду /available"
        )
    else:
        await message.answer("Эта функция доступна только в групповом чате")


@router.message(Command("available"))
async def cmd_available(message: Message):
    if message.chat.type != "private":
        user = message.from_user
        username = user.username
        await rq.set_user_available(username, message.chat.id, True)
        await message.answer(
            "Вы снова в списке ревьюверов. Чтобы больше не быть в нем, вызовите команду /unavailable"
        )
    else:
        await message.answer("Эта функция доступна только в групповом чате")


@router.message(Command("pool"))
async def cmd_pull(message: Message):
    if message.chat.type == "private":
        await message.answer("Пулл доступен только в групповом чате")
        return
    users = await rq.get_active_users(message.chat.id)
    await message.answer(pool_message(users), parse_mode="HTML")


@router.callback_query(F.data == "pool")
async def pull_callback(callback: CallbackQuery):
    if callback.message.chat.type == "private":
        await callback.answer("Пулл доступен только в групповом чате")
        return
    await callback.answer("Текущий пулл")
    users = await rq.get_active_users(callback.message.chat.id)
    await callback.message.answer(pool_message(users), parse_mode="HTML")


@router.message(Command("info"))
async def info(message: Message):
    await message.answer(info_message(), parse_mode="HTML")


@router.callback_query(F.data == "info")
async def info_callback(callback: CallbackQuery):
    await callback.answer("О боте")
    await callback.message.answer(info_message(), parse_mode="HTML")


@router.message(Command("help"))
async def help_command(message: Message):
    answer = "<b>🦾 Список команд</b>\n\n"
    await message.answer(command_list(), parse_mode="HTML")


@router.callback_query(F.data == "help")
async def help_command(callback: CallbackQuery):
    await callback.answer("Команды")
    await callback.message.answer(command_list(), parse_mode="HTML")


url_pattern = re.compile(
    r"(https?://(?:www\.)?git(?:hub|lab)\.\S+|(?:www\.)?git(?:hub|lab)\.\S+)"
)


@router.message(F.chat.type != "private")
async def check_message_for_links(message: Message):
    if (
        message.text is not None
        and url_pattern.search(message.text)
        and not (message.text.startswith("/") or message.text.startswith("!"))
    ):
        user = message.from_user
        username = user.username
        active_users = await rq.get_active_users(message.chat.id)

        if username in active_users:
            active_users.remove(username)

        if len(active_users) < 2:
            return await message.reply("Недостаточно активных пользователей для выбора")

        user_weights = {user: 1.0 for user in active_users}

        last_selected = await rq.get_last_selected(message.chat.id)

        for user in last_selected:
            if user in user_weights:
                user_weights[user] *= 0.5
        print(user_weights)
        users, weights = zip(*user_weights.items())
        print(users, weights)
        first_user = random.choices(users, weights=weights, k=1)[0]
        del user_weights[first_user]
        users, weights = zip(*user_weights.items())
        second_user = random.choices(users, weights=weights, k=1)[0]

        await rq.update_last_selected(message.chat.id, first_user, second_user)

        await message.reply(f"@{first_user} и @{second_user}")
