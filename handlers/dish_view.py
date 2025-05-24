
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.fsm.state import State, StatesGroup

from data import first_course, second_course, grill, salads, drinks, bakery
from handlers.language import user_lang
from handlers.cart import add_to_cart

router = Router()

class PortionState(StatesGroup):
    waiting_for_portion = State()

class DishState(StatesGroup):
    viewing = State()

categories = {
    "category_1": first_course.first_course_items,
    "category_2": second_course.second_course_items,
    "category_3": grill.grill_items,
    "category_4": salads.salads_items,
    "category_5": drinks.drinks_items,
    "category_6": bakery.bakery_items,
}

# 1. После выбора категории — показываем список кнопок с блюдами
@router.callback_query(F.data.in_(categories.keys()))
async def show_dishes(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = user_lang.get(user_id, "ru")
    category = callback.data
    await callback.message.delete()
    await state.update_data(category=category)
    dishes = categories[category]

    builder = InlineKeyboardBuilder()
    for i, dish in enumerate(dishes):
        name = dish.get(f"name_{lang}", dish["name_ru"])
        builder.row(types.InlineKeyboardButton(
            text=name,
            callback_data=f"view_dish_{i}"
        ))
    builder.row(types.InlineKeyboardButton(
        text="🔙 Назад" if lang == "ru" else "🔙 Артқа",
        callback_data="back_to_menu_categories"
    ))
    await callback.message.answer(
        "Выберите блюдо:" if lang == "ru" else "Тағамды таңдаңыз:",
        reply_markup=builder.as_markup()
    )

# 2. После выбора конкретного блюда — показываем карточку
@router.callback_query(F.data.startswith("view_dish_"))
async def view_selected_dish(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = user_lang.get(user_id, "ru")
    index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    category = data["category"]
    dishes = categories[category]
    await state.update_data(index=index)
    await callback.message.delete()
    await send_dish(callback.message, dishes[index], lang, index, len(dishes))

def get_navigation_keyboard(index, total, lang):
    buttons = []
    if index > 0:
        buttons.append(types.InlineKeyboardButton(text="⬅️" + (" Алдыңғы" if lang == "kz" else " Пред."), callback_data="prev_dish"))
    if index < total - 1:
        buttons.append(types.InlineKeyboardButton(text=("Келесі " if lang == "kz" else "След.") + "➡️", callback_data="next_dish"))
    return buttons

def get_action_keyboard(dish, lang):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="✔️ Таңдау" if lang == "kz" else "✔️ Добавить",
            callback_data=f"add_{dish['key']}"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="🛒 Себет" if lang == "kz" else "🛒 Корзина",
            callback_data="show_cart"
        ),
        types.InlineKeyboardButton(
            text="🔙 Артқа" if lang == "kz" else "🔙 Назад",
            callback_data="back_to_menu_categories"
        )
    )
    return builder

async def send_dish(message, dish, lang, index, total):
    name = dish.get(f"name_{lang}", dish["name_ru"])
    description = dish.get(f"description_{lang}", dish["description_ru"])
    price = dish.get("price", 0)
    image_path = dish.get("image")

    text = f"<b>{name}</b>\n{description}\n\n<b>{'Бағасы' if lang == 'kz' else 'Цена'}:</b> {price} ₸"
    builder = InlineKeyboardBuilder()
    builder.row(*get_navigation_keyboard(index, total, lang))
    builder.row(*get_action_keyboard(dish, lang).buttons)
    try:
        photo = FSInputFile(image_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data == "next_dish")
async def next_dish(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("index", 0) + 1
    category = data["category"]
    dishes = categories[category]
    await state.update_data(index=index)
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.delete()
    await send_dish(callback.message, dishes[index], lang, index, len(dishes))

@router.callback_query(F.data == "prev_dish")
async def prev_dish(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("index", 0) - 1
    category = data["category"]
    dishes = categories[category]
    await state.update_data(index=index)
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.delete()
    await send_dish(callback.message, dishes[index], lang, index, len(dishes))

@router.callback_query(F.data.startswith("add_"))
async def ask_portion(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("_", 1)[1]
    data = await state.get_data()
    category = data["category"]
    dishes = categories[category]
    dish = next((d for d in dishes if d["key"] == key), None)

    if not dish:
        await callback.message.answer("Блюдо не найдено.")
        return

    await state.update_data(selected_dish=dish)
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.answer("Сколько порций вы хотите?" if lang == "ru" else "Қанша порция қалайсыз?")
    await state.set_state(PortionState.waiting_for_portion)

@router.message(PortionState.waiting_for_portion)
async def save_portion(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        lang = user_lang.get(message.from_user.id, "ru")
        await message.answer("Введите число." if lang == "ru" else "Сан енгізіңіз.")
        return

    data = await state.get_data()
    dish = data["selected_dish"]
    portion = int(message.text)
    category = data["category"]
    index = data["index"]
    lang = user_lang.get(message.from_user.id, "ru")

    await add_to_cart(user_id=message.from_user.id, dish=dish, portion=portion)

    total_price = dish["price"] * portion
    confirm_text = (
        f"✅ Добавлено: {dish['name_ru']}\n"
        f"Количество: {portion} порции\n"
        f"Общая сумма: {total_price} ₸"
        if lang == "ru" else
        f"✅ Қосылды: {dish['name_kz']}\n"
        f"Саны: {portion} порция\n"
        f"Жалпы баға: {total_price} ₸"
    )

    await message.answer(confirm_text)

    # Повторно отправить текущее блюдо
    dishes = categories[category]
    current_dish = dishes[index]

    # Обновляем состояние: возвращаемся к просмотру
    await state.set_state(DishState.viewing)
    await state.update_data(category=category, index=index)

    await send_dish(message, current_dish, lang, index, len(dishes))