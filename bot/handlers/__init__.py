import importlib
import os

from aiogram import Router

from bot.handlers.start_handler import start_router



routers = [
    start_router
]


# def setup_handlers(dp: Router):
#     """
#     Функция регистрации хендлеров. Сначала регистрирует команды, потом хендлеры, 
#     после этого регистрирует хендлер для неизвестных команд
#     """


#     # Потом все остальные хендлеры
#     handlers_dir = os.path.dirname(__file__)
#     for file in os.listdir(handlers_dir):
#         if file.endswith("_handler.py") or file.endswith("_handlers.py"):
#             module_name = file[:-3]  # Убираем ".py"
#             try:
#                 module = importlib.import_module(f"bot.handlers.{module_name}")
#                 if hasattr(module, "register_handlers"):
#                     module.register_handlers(dp)
#             except Exception as e:
#                 print(f"[ERROR] Не удалось загрузить {module_name}: {e}")

