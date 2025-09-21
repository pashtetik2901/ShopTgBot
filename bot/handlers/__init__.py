import importlib
import os

from aiogram import Router

from bot.handlers.start_handler import start_router
from bot.handlers.pass_callback_handler import pass_callback_router
from bot.handlers.add_product_admin_handler import add_prd_admin_router
from bot.handlers.main_admin_handler import main_admin_router
from bot.handlers.redactor_prd_admin import redactor_prd_admin
from bot.handlers.user_catalog_handler import user_catalog_router
from bot.handlers.cart_hander import cart_router



routers = [
    start_router,
    pass_callback_router,
    add_prd_admin_router,
    main_admin_router,
    redactor_prd_admin,
    user_catalog_router,
    cart_router
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

