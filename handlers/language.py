from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.menu import show_welcome_menu
from handlers.state import user_lang
from handlers.visitors import save_visitor  # добавлено

router = Router()

# Команда /start — выбор языка
@router.message(lambda message: message.text == "/start")
async def start_handler(message: types.Message):
    # Сохраняем пользователя в файл visitors.txt
    save_visitor(message.from_user.id, message.from_user.full_name)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz")]
    ])
    await message.answer(
        "👋 Добро пожаловать в кафе Kaynar!\n\n"
        "🌐 Пожалуйста, выберите язык обслуживания:",
        reply_markup=keyboard
    )

# Обработка выбора языка
@router.callback_query(lambda c: c.data in ["lang_ru", "lang_kz"])
async def process_language(callback: types.CallbackQuery):
    lang = "ru" if callback.data == "lang_ru" else "kz"
    user_id = callback.from_user.id

    # Сохраняем язык пользователя
    user_lang[user_id] = lang

    await callback.message.delete()
    await show_welcome_menu(callback, lang)

# Обработка кнопки «Назад» (⬅️)
@router.callback_query(lambda c: c.data == "back_language")
async def go_back_to_language(callback: types.CallbackQuery):
    await callback.message.delete()
    await start_handler(callback.message)