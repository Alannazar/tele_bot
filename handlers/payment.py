
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
from handlers.language import user_lang
from handlers.cart import user_cart
from handlers.google_sheet_writer import save_full_booking
from datetime import datetime

router = Router()

class PaymentState(StatesGroup):
    choosing_method = State()
    waiting_for_address = State()

@router.callback_query(F.data == "pay")
async def choose_payment_method(callback: types.CallbackQuery, state: FSMContext):
    lang = user_lang.get(callback.from_user.id, "ru")
    text = "Выберите способ оплаты:" if lang == "ru" else "Төлем түрін таңдаңыз:"
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="🚚 Это доставка" if lang == "ru" else "🚚 Бұл жеткізу",
            callback_data="choose_delivery"
        ),
        types.InlineKeyboardButton(
            text="📍 Это бронирование" if lang == "ru" else "📍 Бұл брондау",
            callback_data="choose_booking"
        )
    )
    await callback.message.answer(text, reply_markup=builder.as_markup())
    await state.set_state(PaymentState.choosing_method)

@router.callback_query(F.data == "choose_delivery")
async def ask_address(callback: types.CallbackQuery, state: FSMContext):
    lang = user_lang.get(callback.from_user.id, "ru")
    text = "🚚 Напишите адрес доставки:" if lang == "ru" else "🚚 Жеткізу мекенжайын жазыңыз:"
    await state.set_state(PaymentState.waiting_for_address)
    await state.update_data(from_booking=False)
    await callback.message.answer(text)

@router.message(PaymentState.waiting_for_address)
async def show_qr_after_address(message: types.Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await send_qr_code(message, address=address)
    # state.clear() УДАЛЕНО!

@router.callback_query(F.data == "choose_booking")
async def show_qr_booking(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(from_booking=True)
    await send_qr_code(callback.message)
    # state.clear() УДАЛЕНО!

@router.callback_query(F.data == "payment_confirmed")
async def handle_payment_confirmation(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name
    lang = user_lang.get(user_id, "ru")
    cart = user_cart.get(user_id, [])
    state_data = await state.get_data()

    from_booking = state_data.get("from_booking", False)
    address = state_data.get("address", "-")
    phone = state_data.get("phone", "-")
    date = state_data.get("date", "-")
    time = state_data.get("time", "-")
    people = state_data.get("people", "-")

    total = sum(item.get("price", 0) * item.get("portion", 0) for item in cart)
    items = ", ".join([f"{item.get('name_ru', '—')} x{item.get('portion', 0)}" for item in cart])
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    save_full_booking(
        user_id=user_id,
        username=user_name,
        order_type="Бронирование" if from_booking else "Доставка",
        cart_items=cart,
        total_amount=total,
        booking_info={
            "count": people if from_booking else "-",
            "date": date if from_booking else "-",
            "time": time if from_booking else "-",
            "phone": phone if from_booking else "-",
            "address": address if not from_booking else "-"
        }
    )

    await state.clear()  # Очистка состояния — только здесь, после отправки

    text = "✅ Спасибо за оплату! Отправьте, пожалуйста, чек через WhatsApp." if lang == "ru" else "✅ Төлем үшін рақмет! Түбіртекті WhatsApp арқылы жіберіңіз."
    await callback.message.answer(text)


async def send_qr_code(message: types.Message, address: str = None):
    lang = user_lang.get(message.from_user.id, "ru")
    cart = user_cart.get(message.from_user.id, [])
    total = sum(item.get("price", 0) * item.get("portion", 0) for item in cart)

    caption_parts = []
    if address:
        caption_parts.append(f"📍 <b>Адрес:</b>\n{address}" if lang == "ru" else f"📍 <b>Мекенжай:</b>\n{address}")
    caption_parts.append(f"💵 <b>Итоговая сумма: {total} тг</b>" if lang == "ru" else f"💵 <b>Жалпы сома: {total} тг</b>")
    caption_parts.append(
        "Отсканируйте QR-код Kaspi и нажмите кнопку «Оплатил»." if lang == "ru"
        else "Kaspi QR кодын сканерлеп, «Төледім» батырмасын басыңыз."
    )

    qr_path = "img/payment/payment_kaspi.jpg"
    photo = FSInputFile(qr_path)

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="✅ Оплатил" if lang == "ru" else "✅ Төледім",
            callback_data="payment_confirmed"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="📲 Отправить чек в WhatsApp" if lang == "ru" else "📲 Түбіртекті WhatsApp-қа жіберу",
            url="https://wa.me/7086068647"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="⬅️ Назад" if lang == "ru" else "⬅️ Артқа",
            callback_data="back_to_menu_categories"
        )
    )

    await message.answer_photo(photo=photo, caption="\n\n".join(caption_parts), reply_markup=builder.as_markup(), parse_mode="HTML")