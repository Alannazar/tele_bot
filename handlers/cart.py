from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.language import user_lang

router = Router()

# Хранилище корзины
user_cart = {}

async def add_to_cart(user_id: int, dish: dict, portion: int):
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append({
        "name": dish["name_ru"],
        "name_kz": dish["name_kz"],
        "price": dish["price"],
        "portion": portion
    })

@router.callback_query(lambda c: c.data == "show_cart")
async def show_cart(callback: types.CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    cart = user_cart.get(callback.from_user.id, [])
    if not cart:
        text = "🛒 Ваша корзина пуста." if lang == "ru" else "🛒 Сіздің себетіңіз бос."
        await callback.message.answer(text)
        return

    text = "🛒 <b>Ваша корзина:</b>\n\n" if lang == "ru" else "🛒 <b>Сіздің себетіңіз:</b>\n\n"
    total = 0
    for item in cart:
        name = item["name"] if lang == "ru" else item["name_kz"]
        subtotal = item["price"] * item["portion"]
        total += subtotal
        text += f"🍽 {name} — {item['portion']} × {item['price']} = {subtotal} тг\n"
    text += f"\n💵 <b>Итого: {total} тг</b>" if lang == "ru" else f"\n💵 <b>Жалпы: {total} тг</b>"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить" if lang == "ru" else "💳 Төлеу", callback_data="pay")],
        [InlineKeyboardButton(text="📱 WhatsApp", url="https://wa.me/7086068647")],
        [InlineKeyboardButton(text="📸 Instagram", url="https://www.instagram.com/kaynar_kafe.rudniy/")],
        [InlineKeyboardButton(text="🗑 Очистить корзину" if lang == "ru" else "🗑 Себетті тазалау", callback_data="clear_cart")],
        [InlineKeyboardButton(text="⬅️ Назад" if lang == "ru" else "⬅️ Артқа", callback_data="back_to_menu_categories")]
    ])

    await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    user_cart[callback.from_user.id] = []
    lang = user_lang.get(callback.from_user.id, "ru")
    msg = "🗑 Корзина очищена. Выберите категорию снова." if lang == "ru" else "🗑 Себет тазаланды. Санатты қайта таңдаңыз."
    await callback.message.answer(msg)
    