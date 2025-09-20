from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from bot.config import Config
from functools import wraps

Base = declarative_base()


def get_db_url():
    # Если используется sqlite
    return Config.DB_URL

def get_base():
    return Base

# Создание движка и фабрики сессий
engine = create_async_engine(
    url=get_db_url(),
    echo=Config.DEBUG == False,  # Включает логирование SQL-запросов (для отладки)
    pool_pre_ping=True  # Проверяет соединение перед использованием
)

async_marker = async_sessionmaker(engine)

async def get_connection():
    async with async_marker() as session:
        yield session
        
def with_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async for session in get_connection():
            return await func(*args, session=session, **kwargs)
    return wrapper
        

# Настройка колляции NOCASE при подключении к базе данных
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Настройка подключения к SQLite.
    """
    # Устанавливаем необходимые PRAGMA
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA encoding = 'UTF-8';")
    cursor.execute("PRAGMA case_sensitive_like = OFF;")  # Для регистронезависимого LIKE
    cursor.close()

