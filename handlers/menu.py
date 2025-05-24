from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import FSInputFile

router = Router()

def get_main_keyboard(lang):
    if lang == "kz":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Бронь", callback_data="booking"),
             InlineKeyboardButton(text="📋 Мәзір", callback_data="menu")],
            [InlineKeyboardButton(text="🚗 Жеткізу", callback_data="delivery"),
             InlineKeyboardButton(text="⭐️ Пікірлер", callback_data="reviews")],
            [InlineKeyboardButton(text="📞 WhatsApp", url="https://wa.me/7086068647"),
             InlineKeyboardButton(text="📸 Instagram", url="https://www.instagram.com/kaynar_kafe.rudniy/")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_language")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Бронирование", callback_data="booking"),
             InlineKeyboardButton(text="📋 Меню", callback_data="menu")],
            [InlineKeyboardButton(text="🚗 Доставка", callback_data="delivery"),
             InlineKeyboardButton(text="⭐️ Отзывы", callback_data="reviews")],
            [InlineKeyboardButton(text="📞 WhatsApp", url="https://wa.me/7086068647"),
             InlineKeyboardButton(text="📸 Instagram", url="https://www.instagram.com/kaynar_kafe.rudniy/")],
            [InlineKeyboardButton(text="⬅️ Артқа", callback_data="back_language")]
        ])
    


@router.callback_query(lambda c: c.data == "back_to_main")
async def show_welcome_menu(callback: types.CallbackQuery, lang: str = "ru"):
    photo = FSInputFile("img/kay_1.jpg")
    await callback.message.answer_photo(photo)

    if lang == "kz":
        text = (
            "🍽 <b>Кауар дәмханасына қош келдіңіз!</b>\n\n"
            "🔥 Рудный қаласындағы ең дәмді тағамдар бізде!\n"
            "📖 40 + тан астам дәмді ас мәзірі бар\n"
            "📍 Қостанай облысы, Рудный қ., Ленин к-сі 1/9\n"
            "🚗 Қала ішіндегі жеткізу — бар болғаны 500 т\n\n"
            "👇 Қалағаныңызды таңдаңыз:"
        )
    else:
        text = (
            "🍽 <b>Добро пожаловать в кафе Kaynar!</b>\n\n"
            "🔥 У нас самое вкусное в городе Рудном!\n"
            "📖 Более 40 + блюд на любой вкус\n"
            "📍 Костанайская область, г. Рудный, ул. Ленина 1/9\n"
            "🚗 Доставка по городу — всего за 500 т\n\n"
            "👇 Выберите, что вы хотите:"
        )

    await callback.message.answer(text, reply_markup=get_main_keyboard(lang), parse_mode="HTML")