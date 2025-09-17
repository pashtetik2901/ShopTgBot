import importlib
import os

from aiogram import Router

from bot.handlers.command_handlers import command_router
from bot.handlers.unknown_handler import unknown_router
from bot.handlers.payment_handlers import payment_router
from bot.handlers.technical_support_handlers import technical_router



routers = [
    command_router,
    payment_router,
    technical_router,
    unknown_router
]


def setup_handlers(dp: Router):
    """
    Функция регистрации хендлеров. Сначала регистрирует команды, потом хендлеры, 
    после этого регистрирует хендлер для неизвестных команд
    """

    # Первыми подключаем команды
    dp.include_router(command_router)

    # Потом все остальные хендлеры
    handlers_dir = os.path.dirname(__file__)
    for file in os.listdir(handlers_dir):
        if file.endswith("_handler.py") or file.endswith("_handlers.py"):
            module_name = file[:-3]  # Убираем ".py"
            try:
                module = importlib.import_module(f"bot.handlers.{module_name}")
                if hasattr(module, "register_handlers"):
                    module.register_handlers(dp)
            except Exception as e:
                print(f"[ERROR] Не удалось загрузить {module_name}: {e}")

    # после этого - хендлер для неизвестных команд
    dp.include_router(unknown_router)
