from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🤖 Задать вопрос ИИ")],
            [KeyboardButton(text="🧪 Пройти тест")],
            [KeyboardButton(text="🧑‍💼 Отправить запрос менеджеру")],
        ],
        resize_keyboard=True,
        selective=True,
    )

def back_to_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Главное меню")]],
        resize_keyboard=True,
        selective=True,
    )

def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔑 Установить OpenAI API key", callback_data="admin:set_key")],
            [InlineKeyboardButton(text="🆔 Установить Assistant ID", callback_data="admin:set_assistant")],
            [InlineKeyboardButton(text="📚 Установить Vector Store ID", callback_data="admin:set_vector_store")],
            [InlineKeyboardButton(text="🔄 Привязать Vector Store к Assistant", callback_data="admin:bind_vs")],
            [InlineKeyboardButton(text="📋 Показать текущие настройки", callback_data="admin:show")],
        ]
    )

def test_options_kb(options: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for i, opt in enumerate(options):
        rows.append([InlineKeyboardButton(text=opt, callback_data=f"test:opt:{i}")])
    rows.append([InlineKeyboardButton(text="🏠 В меню", callback_data="test:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
