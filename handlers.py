from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from main import router, last_msg, bot, db, QueryState
from keyboards import kb_all_queries, kb_del_query


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


@router.callback_query(F.data.startswith('del_'))
async def delete_query(call: CallbackQuery):
    """
    Обработчик нажатия на кнопку удаления запроса.
    Удаляет выбранный поисковый запрос из базы данных и обновляет клавиатуру.
    """
    db.delete_query(call.data[4:])
    print(f'удаляем из бызы {call.data[4:]}')
    await call.message.edit_reply_markup(reply_markup=kb_del_query(db.get_query()))
