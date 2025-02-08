from Parser.parser import get_all_announcements, get_announcement, find_new_announcement
from random import choice
from DB.queries import Database

db = Database()


def test_get_all_announcements():
    """
    Тест получения всех объявлений
    """
    print('\nget_all_announcements:')
    for i in get_all_announcements():
        print(i)


def test_get_announcement():
    """
    Тест поучения конкретного объявления
    """
    qwe = choice(db.get_weapon_list())
    link = f'https://gunsbroker.ru{qwe[1]}'
    data = get_announcement(link)
    print('\nget_announcement:')
    print(*data.items(), sep='\n')


def test_find_new_announcement():
    """
    Тест поучения НОВОГО объявления
    """
    data = find_new_announcement()
    print('\nfind_new_announcement:')
    print(data)
