from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from handlers.language import user_lang

router = Router()
REVIEW_CHANNEL_ID = -1002453883295  # KAYNAR_KAFE

class ReviewState(StatesGroup):
    waiting_for_text = State()

@router.callback_query(F.data == "reviews")
async def start_review(callback: types.CallbackQuery, state: FSMContext):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.delete()

    text = (
        "Пожалуйста, оцените наше кафе по 5-балльной шкале:"
        if lang == "ru" else
        "Біздің кафемізді 5 жұлдыз шкаласы бойынша бағалаңыз:"
    )

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="⭐️ 1", callback_data="rate_1"),
            types.InlineKeyboardButton(text="⭐️ 2", callback_data="rate_2"),
            types.InlineKeyboardButton(text="⭐️ 3", callback_data="rate_3"),
            types.InlineKeyboardButton(text="⭐️ 4", callback_data="rate_4"),
            types.InlineKeyboardButton(text="⭐️ 5", callback_data="rate_5"),
        ]
    ])

    await callback.message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("rate_"))
async def capture_rating(callback: types.CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    lang = user_lang.get(callback.from_user.id, "ru")
    await state.update_data(rating=rating, lang=lang)
    await callback.message.delete()

    text = (
        "Спасибо за оценку! Напишите, пожалуйста, пару слов — нам важно ваше мнение."
        if lang == "ru" else
        "Бағалағаныңызға рахмет! Бірнеше пікір қалдырыңыз — бұл біз үшін маңызды."
    )

    await callback.message.answer(text)
    await state.set_state(ReviewState.waiting_for_text)

@router.message(ReviewState.waiting_for_text)
async def handle_review_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    rating = data.get("rating", 0)
    lang = data.get("lang", "ru")
    review_text = message.text
    username = message.from_user.username or f"id:{message.from_user.id}"
    stars = "⭐️" * rating

    # Красивое оформление отзыва
    header = (
        "<b>Новый отзыв о кафе:</b>" if lang == "ru"
        else "<b>Кафе туралы жаңа пікір:</b>"
    )
    footer = f"\n\nОт: @{username}" if lang == "ru" else f"\n\nЖазған: @{username}"

    full_message = f"{header}\n{stars}\n\n{review_text}{footer}"

    try:
        await message.bot.send_message(chat_id=REVIEW_CHANNEL_ID, text=full_message, parse_mode="HTML")
        confirm = (
            "Спасибо! Ваш отзыв опубликован в канале."
            if lang == "ru" else
            "Рақмет! Сіздің пікіріңіз арнада жарияланды."
        )
        await message.answer(confirm)
    except Exception as e:
        await message.answer("Произошла ошибка при отправке отзыва.")
        print("Ошибка отправки в канал:", e)

    await state.clear()