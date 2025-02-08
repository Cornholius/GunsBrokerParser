import requests
from bs4 import BeautifulSoup
from DB.queries import Database

db = Database()


def get_links():
    """
    Берёт из базы все параметры поиска и собирает их в ссылки для запросов.
    :return: Список URL для поисковых запросов.
             Формат: [url1, url2, ...]
    """
    data = db.get_query()
    link_list = []
    for _ in data:
        link = f'https://gunsbroker.ru/search/{_.replace(' ', '%20')}/&cal=0&reloading_type=0&stvol_type=0'
        link_list.append(link)
    return link_list


def get_all_announcements():
    """
    Отправляет запрос на сайт для получения списка всех объявлений.
    :return: Список, содержащий ID объявления и ссылку на объявление.
             Формат: [['id1', 'url1'], ['id2', 'url2'], ...]
    """
    announcements = []
    data = get_links()
    for link in data:
        res = requests.get(link)
        elements = BeautifulSoup(res.text, 'html.parser').select('.main__content > .main__item')
        for element in elements:
            elem_id = element.find('div', {'id': True}).get('id')
            hgroup = element.find('hgroup')
            elem_href = hgroup.find('a').get('href', None)
            announcements.append([elem_id, elem_href])

    return announcements


def get_announcement(link):
    """
    Принимает URL на страницу с товаром и обрабатывает информацию.
    :param link: URL страницы товара (строка).
    :return: Возвращает словарь с информацией о товаре.
             Формат: {'name': 'название', 'city': 'город', 'price': 'цена',
                      'full_description': 'полное описание', 'photo': ['url1', 'url2', ...]}
    """
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'html.parser').select_one('.main__content')
    name = soup.find('h1').get_text()
    city = soup.select_one('.page-product__header--location').find('span').get_text(strip=True)
    price = soup.select_one('.price_h2').get_text()
    text = soup.select_one('.page-product__content--desc').find_all('p')
    description = []
    for i in text:
        description.append(i.get_text(strip=True))
    full_description = ' '.join(description)
    photos = soup.select('.page-product__content--slider-item')
    photo_list = []
    for photo in photos:
        photo_url = photo.find('img').get('src')
        photo_list.append(photo_url)
    result = {
        'name': name,
        'city': city,
        'price': price,
        'full_description': full_description,
        'photo': photo_list
    }
    return result


def find_new_announcement():
    """
    Сравнивает текущие объявления с базой данных и находит новые или удаленные объявления.
    :return: Сообщение о новых или удаленных объявлениях.
             Формат: 'new item: {set_of_new_items}' или 'item solded and need to remove: {set_of_sold_items}'
    """
    db_list = [tuple(item) for item in db.get_weapon_list()]
    list_of_announcements = [tuple(item) for item in get_all_announcements()]
    set_db_list = set(db_list)
    set_list_of_announcements = set(list_of_announcements)

    new_item = set_list_of_announcements.difference(db_list)
    if new_item:
        for i in new_item:
            db.add_to_weapon_list(i)
        return new_item

    solded_item = set_db_list.difference(list_of_announcements)
    if solded_item:
        for i in solded_item:
            db.delete_from_weapon_list(i[0])
