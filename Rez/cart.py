from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from handlers.language import user_lang

router = Router()

# Храним корзины пользователей
user_cart = {}

# Добавить в корзину
async def add_to_cart(user_id: int, name: str, price: int):
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append({"name": name, "price": price})

# Показать корзину
@router.callback_query(lambda c: c.data == "view_cart")
async def view_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = user_lang.get(user_id, "ru")
    cart = user_cart.get(user_id, [])

    # Тексты
    texts = {
        "empty": "🛒 Ваша корзина пуста." if lang == "ru" else "🛒 Сіздің себетіңіз бос.",
        "your_order": "<b>Ваш заказ:</b>" if lang == "ru" else "<b>Сіздің тапсырысыңыз:</b>",
        "total": "Итого" if lang == "ru" else "Жалпы",
        "checkout": "🧾 Оформить заказ" if lang == "ru" else "🧾 Тапсырысты рәсімдеу",
        "clear": "🗑 Очистить" if lang == "ru" else "🗑 Тазалау",
        "back": "⬅️ Назад" if lang == "ru" else "⬅️ Артқа"
    }

    if not cart:
        await callback.message.answer(texts["empty"])
        return

    # Группируем и считаем
    total = 0
    items_summary = {}
    for item in cart:
        name = item["name"]
        price = item["price"]
        total += price
        if name not in items_summary:
            items_summary[name] = {"price": price, "qty": 0}
        items_summary[name]["qty"] += 1

    # Сообщение
    message = texts["your_order"] + "\n"
    for name, data in items_summary.items():
        message += f"- {name} — {data['qty']} шт. — {data['qty'] * data['price']} ₸\n"
    message += f"\n<b>{texts['total']}: {total} ₸</b>"

    # Кнопки
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text=texts["checkout"], callback_data="checkout"),
        types.InlineKeyboardButton(text=texts["clear"], callback_data="clear_cart"),
        types.InlineKeyboardButton(text=texts["back"], callback_data="menu")
    )

    await callback.message.answer(message, reply_markup=builder.as_markup(), parse_mode="HTML")

# Очистить корзину
@router.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_cart[user_id] = []
    lang = user_lang.get(user_id, "ru")
    msg = "🗑 Корзина очищена." if lang == "ru" else "🗑 Себет тазартылды."
    await callback.answer(msg, show_alert=True)
    await view_cart(callback)