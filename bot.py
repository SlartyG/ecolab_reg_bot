import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMINS, TELEGRAM_PROXY
from handlers import registration, admin
from services.sheets import GoogleSheetsService

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN не задан. Укажите его в .env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

session = AiohttpSession(proxy=TELEGRAM_PROXY) if TELEGRAM_PROXY else None
bot = Bot(token=BOT_TOKEN, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(registration.router)
dp.include_router(admin.router)

sheets_service = GoogleSheetsService()


async def hourly_stats_task(bot: Bot, sheets: GoogleSheetsService) -> None:
    """Каждый час отправляет всем админам статистику регистраций за последний час."""
    while True:
        # Ждём до начала следующего часа (например, 15:00), затем раз в час
        now = datetime.now()
        seconds_until_next = (60 - now.minute) * 60 - now.second
        await asyncio.sleep(seconds_until_next)
        try:
            stats = sheets.get_registrations_count_last_hour()
            total = stats["events"] + stats["accelerator"]
            text = (
                "📊 Статистика за последний час\n\n"
                f"Мероприятия: {stats['events']}\n"
                f"Акселератор: {stats['accelerator']}\n"
                f"Всего: {total}"
            )
            for admin_id in ADMINS:
                try:
                    await bot.send_message(admin_id, text)
                except Exception as e:
                    logger.warning("Failed to send hourly stats to admin %s: %s", admin_id, e)
        except Exception as e:
            logger.exception("Hourly stats task error: %s", e)
        await asyncio.sleep(3600)


async def main():
    logger.info("Starting bot...")
    if TELEGRAM_PROXY:
        proxy_host = TELEGRAM_PROXY.rsplit("@", 1)[-1]
        logger.info("Telegram proxy enabled: %s", proxy_host)
    else:
        logger.warning(
            "TELEGRAM_PROXY не задан. Если api.telegram.org недоступен с сервера, "
            "бот не сможет подключиться."
        )
    asyncio.create_task(hourly_stats_task(bot, sheets_service))
    while True:
        try:
            await dp.start_polling(bot)
            break
        except TelegramNetworkError as e:
            logger.error("Telegram network error, retry in 30s: %s", e)
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())