def get_all_announcements(links):
    announcements = []
    for link in links:
        res = requests.get(link)
        elements = BeautifulSoup(res.text, 'html.parser').select('div.main__item')
        print(len(elements))
        for element in elements:
            # Удаление ненужного блока div
            trash = element.find('div', {'class': 'p-3'})
            if trash:
                trash.decompose()

            # Поиск идентификатора элемента
            elem_id_div = element.find('div', {'id': True})
            if elem_id_div:
                elem_id = elem_id_div.get('id')
            else:
                print("Element with ID not found")
                continue  # Пропустить этот элемент, если ID не найден

            # Поиск ссылки внутри элемента
            hgroup = element.find('h1')  # Замените на правильный тег, если это необходимо
            if hgroup:
                elem_href = hgroup.find('a')
                if elem_href:
                    elem_href = elem_href.get('href', None)
                else:
                    print("Link not found inside hgroup")
                    continue  # Пропустить этот элемент, если ссылка не найдена
            else:
                print("Hgroup element not found")
                continue  # Пропустить этот элемент, если hgroup не найден

            announcements.append([elem_id, elem_href])

    return announcements