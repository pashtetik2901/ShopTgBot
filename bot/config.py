import json
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Загрузка переменных окружения
if os.path.exists(os.path.join(BASE_DIR, '.env.local')):
    load_dotenv(os.path.join(BASE_DIR, '.env.local'))
else:
    load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    DB_URL = f"sqlite+aiosqlite:///{BASE_DIR}/db/{os.getenv('DB_NAME')}"
    ADMIN_IDS = json.loads(os.getenv('ADMIN_IDS', '[]'))
    SCHEDULER = os.getenv('SCHEDULER', 'False').lower() in ('true', '1', 'yes', 'on')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')

    # Настройка логов
    # минимальный уровень логов
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    # кол-во дней хранения логов
    LOG_ROTATE_DAYS = int(os.getenv('LOG_ROTATE_DAYS', 15))
    # Размер файла логов в мегабайтах
    LOG_ROTATE_SIZE_MB = int(os.getenv('LOG_ROTATE_SIZE_MB', 10))
    FORMAT_LOG = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"

    # ключ платежного шлюза, выпущенный через BotFather
    PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')

    # настройки для работы с гугл таблицами/дисками
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE')

    #айдишник для гугл таблицы
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')