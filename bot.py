import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

# Роутеры
from handlers import language, menu, booking, menu_categories
from handlers import cart
from handlers import dish_view
from handlers import payment
from handlers.delivery_menu import router as delivery_router
from handlers import reviews

# Загрузка переменных среды
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки Webhook
WEBHOOK_PATH = "/webhook"
WEBHOOK_HOST = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

dp.include_routers(
    language.router,
    menu.router,
    booking.router,
    menu_categories.router,
    cart.router,
    dish_view.router,
    payment.router,
    delivery_router,
    reviews.router
)

async def on_startup(app):
    logging.warning("Запуск бота...")
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    logging.warning("Остановка бота...")
    await bot.delete_webhook()

def main():
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    app["bot"] = bot

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))