from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.google_sheet_writer import save_full_booking  # импорт функции для записи в таблицу

router = Router()

class BookingState(StatesGroup):
    waiting_for_people = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_contact = State()

@router.callback_query(F.data == "booking")
async def booking_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("👥 Сколько человек вы хотите забронировать?")
    await state.set_state(BookingState.waiting_for_people)

@router.message(BookingState.waiting_for_people)
async def booking_people(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число.")
        return
    await state.update_data(people=message.text)
    await message.answer("📅 На какую дату вы хотите забронировать? (например: 2024-06-01)")
    await state.set_state(BookingState.waiting_for_date)

@router.message(BookingState.waiting_for_date)
async def booking_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("🕓 Во сколько вы хотите прийти? (например: 18:30)")
    await state.set_state(BookingState.waiting_for_time)

@router.message(BookingState.waiting_for_time)
async def booking_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer("📱 Пожалуйста, напишите номер телефона.")
    await state.set_state(BookingState.waiting_for_contact)

@router.message(BookingState.waiting_for_contact)
async def booking_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    # Сохраняем в Google Таблицу
    save_full_booking(
    user_id=user_id,
    username=username,
    order_type="Бронирование",
    cart_items=[],
    total_amount=0,
    booking_info={
        "count": data.get("people"),
        "date": data.get("date"),
        "time": data.get("time"),
        "phone": data.get("contact")
    }
)
    # Кнопки меню и WhatsApp
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🍽 Перейти к меню", callback_data="menu"),
        types.InlineKeyboardButton(text="💬 Написать в WhatsApp", url="https://wa.me/7086068647")
    )

    # Финальное сообщение с данными
    text = (
        "✅ Спасибо! Ваше бронирование сохранено:\n\n"
        f"👥 Кол-во человек: {data.get('people')}\n"
        f"📅 Дата: {data.get('date')}\n"
        f"🕓 Время: {data.get('time')}\n"
        f"📱 Телефон: {data.get('contact')}\n\n"
        "Теперь выберите блюда из меню или свяжитесь с нами:"
    )

    await message.answer(text, reply_markup=builder.as_markup())