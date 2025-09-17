from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.jobs.example_job import EverydayJob


class JobScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start_jobs(self, bot: Bot):
        """
        Запускает все фоновые задачи.
        """
        # Пример постановки задачи в очередь
        self.scheduler.add_job(EverydayJob.start, "interval", seconds=300, kwargs={"bot": bot})

        self.scheduler.start()


    async def stop_jobs(self):
        if self.scheduler.running:  # Проверяем, запущен ли планировщик
            self.scheduler.shutdown(wait=False)  # Останавливаем планировщик без ожидания завершения задач


