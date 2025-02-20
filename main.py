import asyncio
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.storage.memory import MemoryStorage
from DB.queries import Database
from Parser.parser import find_new_announcement, get_announcement
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


API_TOKEN = '7606037464:AAGJx5nCVO2ffW8HCinc31ElNf3XzZrVcLA'
ADMIN_CHAT_ID = '1272900243'
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


@router.message(F.text == '/list')
async def get_queries(message: types.Message):
    """
    Обработчик команды /list.
    Отображает список действующих поисковых запросов или сообщает, что их нет.
    """
    if last_msg:
        for i in last_msg:
            await bot.delete_message(message.chat.id, i)
        last_msg.clear()
    queries = db.get_query()
    if queries:
        text = 'Действующие поисковые запросы:'
        keyboard = kb_all_queries(queries)
        msg = await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)
    else:
        text = "Нет сохраненных запросов."
        msg = await bot.send_message(chat_id=message.chat.id, text=text)
    last_msg.append(message.message_id)
    last_msg.append(msg.message_id)


@router.message(F.text == '/add')
async def add_query(message: types.Message, state: FSMContext):
    """
    Обработчик команды /add.
    Запускает процесс добавления нового поискового запроса.
    """
    if last_msg:
        for i in last_msg:
            await bot.delete_message(message.chat.id, i)
        last_msg.clear()
    text = "Введите поисковый запрос:"
    msg = await bot.send_message(chat_id=message.chat.id, text=text)
    await state.set_state(QueryState.query)
    last_msg.append(message.message_id)
    last_msg.append(msg.message_id)


@router.message(F.text, QueryState.query)
async def process_add_query(message: types.Message, state: FSMContext):
    """
    Обработчик ввода поискового запроса.
    Сохраняет введенный запрос в базу данных и отправляет подтверждение пользователю.
    Очищает состояние FSM после завершения.
    """
    await state.update_data(query=message.text)
    data = await state.get_data()
    result = db.add_query(data['query'])
    msg = await message.answer(text=result)
    last_msg.append(message.message_id)
    last_msg.append(msg.message_id)
    await state.clear()


@router.message(F.text == '/del')
async def del_queries(message: types.Message):
    """
    Обработчик команды '/del'.
    Отображает список сохраненных поисковых запросов и предлагает пользователю удалить один из них.
    Если нет сохраненных запросов, отправляет сообщение об отсутствии запросов.
    :param message: Объект сообщения от пользователя.
    """
    if last_msg:
        for i in last_msg:
            await bot.delete_message(message.chat.id, i)
        last_msg.clear()
    queries = db.get_query()
    if queries:
        text = 'Какой запрос удалить?:'
        keyboard = kb_del_query(queries)
        msg = await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)
    else:
        text = "Нет сохраненных запросов."
        msg = await bot.send_message(chat_id=message.chat.id, text=text)
    last_msg.append(message.message_id)
    last_msg.append(msg.message_id)


def kb_all_queries(queries):
    """
    Создает клавиатуру с кнопками для каждого поискового запроса.
    :param queries: Список поисковых запросов.
    :return: Объект InlineKeyboardMarkup.
    """
    inline_kb_list = [[InlineKeyboardButton(text=f"{query}", callback_data=f'srh_{query}')] for query in queries]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def kb_del_query(queries):
    """
    Создает клавиатуру для удаления поисковых запросов.
    Каждая кнопка на клавиатуре соответствует одному поисковому запросу и имеет уникальный
    callback_data для обработки нажатия.
    Возвращает объект InlineKeyboardMarkup с кнопками, расположенными в виде списка списков.
    :param queries: Список поисковых запросов.
    :return: Объект InlineKeyboardMarkup.
    """
    inline_kb_list = [[InlineKeyboardButton(text=f"{query}", callback_data=f'del_{query}')] for query in queries]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


@router.callback_query(F.data.startswith('del_'))
async def delete_query(call: CallbackQuery):
    """
    Обработчик нажатия на кнопку удаления запроса.
    Удаляет выбранный поисковый запрос из базы данных и обновляет клавиатуру.
    """
    db.delete_query(call.data[4:])
    print(f'удаляем из бызы {call.data[4:]}')
    await call.message.edit_reply_markup(reply_markup=kb_del_query(db.get_query()))


async def find_new_announcements():
    """
    Функция для поиска новых объявлений.
    Выполняет поиск новых объявлений и отправляет их администратору бота.
    """
    print('start searching...')
    new_announcements = find_new_announcement()
    if new_announcements:
        for announcement in new_announcements:
            data = get_announcement(announcement[1])
            photos = data['photo']
            message_text = (
                f"<b>{data['name']}</b>\n\n"
                f"<b><code>Город:</code></b>  {data['city']}\n"
                f"<code>Цена:</code>  {data['price']}\n\n"
                f"{data['full_description']}"
            )
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_text)

            # Разделяем список фотографий на части по 10 штук иначе телега не пропустит
            for i in range(0, len(photos), 10):
                chunk = photos[i:i + 10]
                media_group = [types.InputMediaPhoto(type='photo', media=photo) for photo in chunk]
                await bot.send_media_group(chat_id=ADMIN_CHAT_ID, media=media_group)


if __name__ == "__main__":
    asyncio.run(main())
