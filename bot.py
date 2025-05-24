import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import language, menu, booking, menu_categories
from dotenv import load_dotenv
from handlers import language, menu, booking, menu_categories
from handlers import cart
# from handlers import first_course_view
from handlers import dish_view
from handlers import payment
from handlers.delivery_menu import router as delivery_router
from handlers import reviews

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключаем все роутеры
dp.include_routers(
    language.router,
    menu.router,
    booking.router,
    menu_categories.router,
    # first_course_handler.router,
    cart.router,
    # first_course_view.router,
    dish_view.router,
    payment.router,
    delivery_router,
    reviews.router  # добавлено
)

# Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())