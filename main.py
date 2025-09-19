import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from bot.config import Config
# from bot.handlers import setup_handlers
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.jobs import JobScheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()          # Логирование в консоль
    ]
)

# Инициализация бота и диспетчера
bot = Bot(
    token=Config.TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация обработчиков
# setup_handlers(dp)

# Запуск бота
async def main():
    scheduller = None
    try:
        logging.info("Бот запущен")

        from bot.handlers import routers

        for router in routers:
            dp.include_router(router)
            logging.info(f'Router - {router}, connected')

        if Config.SCHEDULER == True:
            scheduller = JobScheduler()
            # Запускаем планировщик задач
            await scheduller.start_jobs(bot=bot)

        # Запускаем бота
        await dp.start_polling(bot, skip_updates=True)

    except Exception as e:
        logging.error(f"Ошибка запуска бота: {e}")

    finally:
        if Config.SCHEDULER == True and scheduller:
            await scheduller.stop_jobs()
        logging.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())