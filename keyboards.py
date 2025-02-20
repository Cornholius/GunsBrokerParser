from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
