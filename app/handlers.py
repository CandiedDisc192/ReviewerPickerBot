import re
import random
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from collections import deque
import app.keyboards as kb
from app.client_data import get_chat_members
import app.db.requests as rq

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.chat.type != "private":
        await message.reply('<b>Привет!</b> Я помогу назначить двух случайных участников этого чата на проверку MR.',
                            reply_markup=kb.catalog, parse_mode='HTML')
        await message.reply("Подождите, собираю информацию об участниках чата...")
        await get_chat_members(message.chat.id)
        await message.reply("Бот готов к работе")
    else:
        await message.reply(
            '<b>Привет!</b>\nЯ помогу назначить двух случайных участников чата на проверку MR.\nПросто добавьте меня '
            'в ваш рабочий чат и напишите команду /start.',
            reply_markup=kb.catalog, parse_mode='HTML')


@router.message(Command('unavailable'))
async def cmd_unavailable(message: Message):
    if message.chat.type != "private":
        user = message.from_user
        username = user.username
        await rq.set_user_available(username, message.chat.id, False)
        await message.answer('Вы больше не в списке ревьюверов. Чтобы вернуться в него, вызовите команду /available')
    else:
        await message.answer('Эта функция доступна только в групповом чате')


@router.message(Command('available'))
async def cmd_available(message: Message):
    if message.chat.type != "private":
        user = message.from_user
        username = user.username
        await rq.set_user_available(username, message.chat.id, True)
        await message.answer('Вы снова в списке ревьюверов. Чтобы больше не быть в нем, вызовите команду /unavailable')
    else:
        await message.answer('Эта функция доступна только в групповом чате')


@router.message(Command('pool'))
async def cmd_pull(message: Message):
    if message.chat.type != "private":
        active_users = await rq.get_active_users(message.chat.id)
        answer = "<b>📋 Текущий пулл</b>\n\n"
        new_users = list(map(lambda x: f'<code>{x}</code>', active_users))
        answer += ', '.join(new_users)
        await message.answer(answer, parse_mode='HTML')
    else:
        await message.answer("Пулл доступен только в групповом чате")


@router.message(Command('help'))
async def help_command(message: Message):
    answer = "<b>🦾 Список команд</b>\n\n"
    cmds = [
        '/start — Запустить бота',
        '/available — Сделать себя доступным для ревью',
        '/unavailable — Сделать себя недоступным для ревью',
        '/pool — Вывести пулл доступных для ревью участников',
        '/help — Вывести список команд'
    ]
    answer += '\n'.join(cmds)
    await message.answer(answer, parse_mode='HTML')


@router.message(Command('info'))
async def info(message: Message):
    answer = "ℹ️ Этот бот помогает автоматически назначать двух человек на ревью MR. \n\n" + \
             "Просто добавьте бота в ваш рабочий чат и напишите команду /start. " + \
             ("Tеперь на все сообщения, содержащие <code>ссылку</code>, будут назначаться два рандомных человека из "
              "группы, кроме автора сообщения.") + \
             ("Если вы скидываете ссылку не с целью запроса ревью на нее, начните сообщение с <code>!</code> и бот не "
              "отреагирует на нее.\n\n") + \
             ("Есть возможность посмотреть список всех доступных для ревью участников, для этого выберите <b>📋 "
              "Текущий пулл</b> в меню.\n\n") + \
             "Чтобы убрать себя из списка вызовите команду /unavailable, чтобы вернуться — /available."

    await message.answer(answer, parse_mode='HTML')


@router.callback_query(F.data == 'info')
async def info(callback: CallbackQuery):
    await callback.answer('О боте')
    message = "ℹ️ Этот бот помогает автоматически назначать двух человек на ревью MR. \n\n" + \
              "Просто добавьте бота в ваш рабочий чат и напишите команду /start. " + \
              ("Теперь на все сообщения, содержащие ссылку, будут назначаться два рандомных человека из группы, "
               "кроме автора сообщения.") + \
              ("Если вы скидываете ссылку не с целью запроса ревью на нее, начните сообщение с ! и бот не отреагирует "
               "на нее.\n\n") + \
              ("Есть возможность посмотреть список всех доступных для ревью участников, для этого выберите 📋 Текущий "
               "пулл в меню.\n\n") + \
              "Чтобы убрать себя из списка вызовите команду /unavailable, чтобы вернуться — /available."
    await callback.message.answer(message, parse_mode='HTML')


@router.callback_query(F.data == 'pool')
async def pull(callback: CallbackQuery):
    active_users = await rq.get_active_users(callback.message.chat.id)
    if callback.message.chat.type != "private":
        await callback.answer("Текущий пулл")
        message = "<b>📋 Текущий пулл</b>\n\n"
        new_users = list(map(lambda x: f'<code>{x}</code>', active_users))
        message += ', '.join(new_users)
        await callback.message.answer(message, parse_mode='HTML')
    else:
        await callback.answer("Пулл доступен только в групповом чате")


@router.callback_query(F.data == 'commands')
async def commands(callback: CallbackQuery):
    await callback.answer('Команды')
    message = "<b>🦾 Список команд</b>\n\n"
    cmds = [
        '/start — Запустить бота',
        '/help — Вывести список команд',
        '/info — Вывести информацию о боте',
        '/pool — Вывести пулл доступных для ревью участников',
        '/available — Сделать себя доступным для ревью',
        '/unavailable — Сделать себя недоступным для ревью'
    ]
    message += '\n'.join(cmds)
    await callback.message.answer(message, parse_mode='HTML')


url_pattern = re.compile(
    r'(https?://(?:www\.)?\S+)|(www\.\S+)'
)

LAST_SELECTED = deque(maxlen=4)


@router.message(F.chat.type != "private")
async def check_message_for_links(message: Message):
    if message.text is not None and url_pattern.search(message.text) and not (
            message.text.startswith('/') or message.text.startswith('!')):
        user = message.from_user
        username = user.username
        active_users = await rq.get_active_users(message.chat.id)

        if username in active_users:
            active_users.remove(username)

        if len(active_users) < 2:
            return await message.reply("Недостаточно активных пользователей для выбора")

        user_weights = {user: 1.0 for user in active_users}

        for user in LAST_SELECTED:
            if user in user_weights:
                user_weights[user] *= 0.5

        users, weights = zip(*user_weights.items())

        first_user = random.choices(users, weights=weights, k=1)[0]
        del user_weights[first_user]
        users, weights = zip(*user_weights.items())

        second_user = random.choices(users, weights=weights, k=1)[0]
        LAST_SELECTED.append(first_user)
        LAST_SELECTED.append(second_user)

        await message.reply(f'@{first_user} и @{second_user}')
