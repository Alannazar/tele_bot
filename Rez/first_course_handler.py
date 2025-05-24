from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.first_course import first_course_items
from handlers.language import user_lang

router = Router()
user_cart = {}

@router.callback_query(lambda c: c.data == "category_1")
async def show_first_course(callback: types.CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")

    if lang == "kz":
        text = (
            "🥄 <b>Бірінші тағамдар</b>\n"
            "🔥 Ең дәмді сорпалар мен ыстық тағамдар!\n"
            "👇 Таңдауыңызды төменнен таңдаңыз:"
        )
        cart_text = "🛒 Менің себетім"
        back_text = "⬅️ Артқа"
    else:
        text = (
            "🥄 <b>Первые блюда</b>\n"
            "🔥 Наваристые супы и горячие блюда!\n"
            "👇 Выберите понравившееся:"
        )
        cart_text = "🛒 Моя корзина"
        back_text = "⬅️ Назад"

    builder = InlineKeyboardBuilder()
    row = []

    for index, item in enumerate(first_course_items, 1):
        name = item["name_kz"] if lang == "kz" else item["name_ru"]
        emoji = get_emoji(name)
        row.append(types.InlineKeyboardButton(
            text=f"{emoji} {name}",
            callback_data=f"add_{name}"
        ))

        if index % 2 == 0:
            builder.row(*row)
            row = []

    if row:
        builder.row(*row)

    builder.row(
        types.InlineKeyboardButton(text=cart_text, callback_data="show_cart"),
        types.InlineKeyboardButton(text=back_text, callback_data="back_to_menu")
    )

    await callback.message.answer(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(lambda c: c.data == "show_cart")
async def show_cart_callback(callback: types.CallbackQuery):
    from handlers.cart import show_cart
    await show_cart(callback)

@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu_callback(callback: types.CallbackQuery):
    from handlers.menu_categories import show_menu_categories
    await show_menu_categories(callback)

def get_emoji(name: str) -> str:
    emojis = {
        "Суп из чечевицы": "🥣", "Жасымық сорпасы": "🥣",
        "Борщ": "🍅",
        "Куриный суп": "🐔", "Тауық сорпасы": "🐔",
        "Солянка": "🍲",
        "Шурпа": "🥘",
        "Окрошка": "❄️",
        "Крем-суп грибной": "🍄", "Саңырауқұлақ крем-сорпасы": "🍄"
    }
    return emojis.get(name, "🍽")