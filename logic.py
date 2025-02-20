from aiogram import types

from Parser.parser import find_new_announcement, get_announcement
from main import bot, ADMIN_CHAT_ID


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
