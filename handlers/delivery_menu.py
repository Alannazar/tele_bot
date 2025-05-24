from aiogram import Router, types
from handlers.language import user_lang
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.callback_query(lambda c: c.data == "delivery")
async def handle_delivery(callback: types.CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")

    builder = InlineKeyboardBuilder()
    if lang == "kz":
        builder.row(
            types.InlineKeyboardButton(text="🥣 1-ші тағам", callback_data="category_1"),
            types.InlineKeyboardButton(text="🥗 Салаттар", callback_data="category_4"),
            types.InlineKeyboardButton(text="🥟 Тапсымалар", callback_data="category_6")
        )
        builder.row(
            types.InlineKeyboardButton(text="🍛 2-ші тағам", callback_data="category_2"),
            types.InlineKeyboardButton(text="🍖 Шашлықтар", callback_data="category_3"),
            types.InlineKeyboardButton(text="🥤 Сусындар", callback_data="category_5")
        )
        builder.row(
            types.InlineKeyboardButton(text="🟢 Байланыс", url="https://wa.me/7086068647")
        )
        builder.row(
            types.InlineKeyboardButton(text="↩️ Артқа", callback_data="back_to_main")
        )
        text = (
            "<b>Мәзір бөлімін таңдаңыз:</b>\n"
            "🍽️ <i>Біздің ең дәмді тағамдарымызды таңдаңыз.</i>\n\n"
            "⬇️ Қалаған санатты таңдаңыз:"
        )
    else:
        builder.row(
            types.InlineKeyboardButton(text="🥣 1-е блюдо", callback_data="category_1"),
            types.InlineKeyboardButton(text="🥗 Салаты", callback_data="category_4"),
            types.InlineKeyboardButton(text="🥟 Выпечка", callback_data="category_6")
        )
        builder.row(
            types.InlineKeyboardButton(text="🍛 2-е блюдо", callback_data="category_2"),
            types.InlineKeyboardButton(text="🍖 Шашлыки", callback_data="category_3"),
            types.InlineKeyboardButton(text="🥤 Напитки", callback_data="category_5")
        )
        builder.row(
            types.InlineKeyboardButton(text="🟢 Контакты", url="https://wa.me/7086068647")
        )
        builder.row(
            types.InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main")
        )
        text = (
            "<b>Выберите категорию меню:</b>\n"
            "🍽️ <i>Самые вкусные блюда только у нас!</i>\n\n"
            "⬇️ Выберите категорию:"
        )

    await callback.message.delete()
    await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")