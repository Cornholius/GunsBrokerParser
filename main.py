import asyncio
import json
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.storage.memory import MemoryStorage
from DB.queries import Database
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.state import State, StatesGroup
from logic import find_new_announcements


with open('config.json', 'r') as file:
    config = json.load(file)

API_TOKEN = config['API_TOKEN']
ADMIN_CHAT_ID = config['ADMIN_CHAT_ID']
# API_TOKEN = '7606037464:AAGJx5nCVO2ffW8HCinc31ElNf3XzZrVcLA'
# ADMIN_CHAT_ID = '1272900243'
last_msg = []
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
db = Database()
router = Router()
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


class QueryState(StatesGroup):
    query = State()


async def main():
    """
    Основная функция для запуска бота.
    Ставит на выполнение задачу поиска новых объявлений каждый час,
    добавляет роутер к диспетчеру, удаляет вебхук и начинает поллинг бота.
    """
    await find_new_announcements()
    scheduler.add_job(find_new_announcements, 'interval', seconds=3600)
    scheduler.start()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
