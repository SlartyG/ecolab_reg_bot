import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMINS
from handlers import registration, admin
from services.sheets import GoogleSheetsService

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN не задан. Укажите его в .env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
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
    asyncio.create_task(hourly_stats_task(bot, sheets_service))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())