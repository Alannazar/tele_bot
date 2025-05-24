import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import language, menu, booking, menu_categories
from dotenv import load_dotenv
from handlers import language, menu, booking, menu_categories, first_course_handler
from handlers import cart

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
    first_course_handler.router,
    cart.router # добавлено
)

# Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())