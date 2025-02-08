import asyncio

from aiogram.filters import CommandStart, Command

from DB.queries import Database
from Parser.parser import find_new_announcement
from aiogram import Bot, Dispatcher, types, Router

API_TOKEN = '1174022654:AAH7z59i2Y3reHEdvHowSbbTrBpueP1cmxs'
ADMIN_CHAT_ID = '1272900243'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
db = Database()
router = Router()


async def main():
    # scheduler.add_job(send_time_msg, 'interval', seconds=10)
    # scheduler.start()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для поиска объявлений на сайте GunsBroker.")


@router.message(Command('запрос'))
async def add_query(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(chat_id=message.chat.id,
                               text="Введите поисковый запрос:")
        # Установить состояние ожидания ввода запроса
        dp.register_next_step_handler(message, process_add_query)


async def process_add_query(message: types.Message):
    query = message.text
    result = db.add_query(query)
    await bot.send_message(chat_id=message.chat.id,
                           text=result)


@router.message(Command('все запросы'))
async def get_queries(message: types.Message):
    if message.chat.type == 'private':
        queries = db.get_query()
        if queries:
            for query in queries:
                await bot.send_message(chat_id=message.chat.id,
                                       text=f"Запрос: {query}")
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text="Нет сохраненных запросов.")


async def find_new_announcements():
        new_announcements = find_new_announcement()
        if new_announcements:
            for announcement in new_announcements:
                await bot.send_message(chat_id=ADMIN_CHAT_ID,
                                       text=f"Найдено новое объявление: {announcement[1]}")


async def scheduler():
    while True:
        await asyncio.sleep(10)  # Запуск каждые пол часа
        await find_new_announcements()


if __name__ == "__main__":
    asyncio.run(main())