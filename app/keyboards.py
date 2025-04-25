from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

catalog = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="info"),
            InlineKeyboardButton(text="📋 Текущий пулл", callback_data="pool"),
        ],
        [InlineKeyboardButton(text="🦾 Список команд", callback_data="commands")],
    ]
)
