import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from DB.queries import Database
from Parser.parser import find_new_announcement
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


API_TOKEN = '7606037464:AAGJx5nCVO2ffW8HCinc31ElNf3XzZrVcLA'
ADMIN_CHAT_ID = '1272900243'

last_msg = {}
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
db = Database()
router = Router()
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


class QueryState(StatesGroup):
    query = State()


async def main():
    # scheduler.add_job(find_new_announcements, 'interval', seconds=10)
    # scheduler.start()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



@router.message(CommandStart())
async def send_welcome(message: types.Message):
    last_msg[message.chat.id] = message.message_id
    if last_msg:
        for i in last_msg:
            await bot.delete_message(message.chat.id, last_msg[message.chat.id])
    msg = await message.reply("Привет! Я бот для поиска объявлений на сайте GunsBroker. Напиши /start для начала работы")
    last_msg[message.chat.id] = msg.message_id


@router.message(F.text == '/list')
async def get_queries(message: types.Message):
    last_msg[message.chat.id] = message.message_id
    if last_msg:
        for i in last_msg:
            await bot.delete_message(message.chat.id, last_msg[message.chat.id])
    queries = db.get_query()
    if queries:
        msg = await bot.send_message(chat_id=message.chat.id,
                               text='Действующие поисковые запросы:',
                               reply_markup=kb_all_queries(queries))
    else:
        msg = await bot.send_message(chat_id=message.chat.id,
                               text="Нет сохраненных запросов.")
    last_msg[message.chat.id] = msg.message_id

@router.message(F.text == '/add')
async def add_query(message: types.Message, state: FSMContext):
    last_msg[message.chat.id] = message.message_id
    if last_msg:
        for i in last_msg:
            await bot.delete_message(message.chat.id, last_msg[message.chat.id])
    msg = await bot.send_message(chat_id=message.chat.id, text="Введите поисковый запрос:")
    await state.set_state(QueryState.query)
    last_msg[message.chat.id] = msg.message_id


@router.message(F.text, QueryState.query)
async def process_add_query(message: types.Message, state: FSMContext):
    await state.update_data(query=message.text)
    data = await state.get_data()
    result = db.add_query(data['query'])
    msg = await message.answer(text=result)
    last_msg[message.chat.id] = message.message_id
    last_msg[message.chat.id] = msg.message_id
    await state.clear()

# @router.message(state=QueryState.waiting_for_query)
# async def process_add_query(message: types.Message, state: FSMContext):
#     query = message.text
#     result = db.add_query(query)
#     msg = await message.reply(text=result)
#     last_msg[message.chat.id] = msg.message_id
#     await state.clear()





@router.message(F.text == '/del')
async def del_queries(message: types.Message):
    last_msg[message.chat.id] = message.message_id
    if last_msg:
        for i in last_msg:
            await bot.delete_message(message.chat.id, last_msg[message.chat.id])
    if message.chat.type == 'private':
        queries = db.get_query()
        if queries:
            msg =await bot.send_message(chat_id=message.chat.id,
                                   text='Какой запрос удалить?:',
                                   reply_markup=kb_del_query(queries))
        else:
            msg =await bot.send_message(chat_id=message.chat.id,
                                   text="Нет сохраненных запросов.")
        last_msg[message.chat.id] = msg.message_id


def kb_all_queries(queries):
    inline_kb_list = [[InlineKeyboardButton(text=f"{query}", callback_data=f'srh_{query}')] for query in queries]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def kb_del_query(queries):
    inline_kb_list = [[InlineKeyboardButton(text=f"{query}", callback_data=f'del_{query}')] for query in queries]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


@router.callback_query(F.data.startswith('del_'))
async def delete_query(call: CallbackQuery):
    db.delete_query(call.data[4:])
    print(f'удаляем из бызы {call.data[4:]}')
    await call.message.edit_reply_markup(reply_markup=kb_del_query(db.get_query()))


async def find_new_announcements():
    print('start searching...')
    new_announcements = find_new_announcement()
    if new_announcements:
        for announcement in new_announcements:
            await bot.send_message(chat_id=ADMIN_CHAT_ID,
                                   text=f"Найдено новое объявление: {announcement[1]}")




if __name__ == "__main__":
    asyncio.run(main())
