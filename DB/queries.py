import sqlite3


class Database:

    def __init__(self) -> None:
        self.conn = sqlite3.connect("./DB/db.db")

    def add_query(self, query) -> str:
        """
        Добавляет поисковый запрос в базу данных, который в дальнейшем будет использоваться для поиска на сайте.
        :param query: Поисковой запрос (строка).
        :return: Строка с результатом выполнения операции (например, "OK" или сообщение об ошибке).
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO queries (query) VALUES (?)", (query,))
            return 'Запрос добавлен'

    def get_query(self) -> list[str, ...]:
        """
        Получает все поисковые запросы из базы данных.
        :return: Список строк [str, str], содержащих значения из столбца `query` таблицы `queries`.
        """
        with self.conn:
            cursor = self.conn.cursor()
            query = cursor.execute('SELECT query FROM queries').fetchall()
            result = [i[0] for i in query]
            return result

    def delete_query(self, query_id) -> None:
        """
        Удаляет поисковый запрос из базы данных по его идентификатору.
        :param query_id: str. Идентификатор поискового запроса для удаления.
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM queries WHERE id = ?', (query_id,))

    def add_to_weapon_list(self, weapon) -> None:
        """
        Добавляет page id и url объявления в таблицу `weapon_list` базы данных.
        :param weapon: Кортеж, содержащий идентификатор страницы и URL оружия.
                       Формат: (page_id, url)
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO weapon_list (page_id, url) VALUES (?, ?)",
                           (weapon[0], weapon[1],))

    def get_weapon_list(self) -> list[[str, str], ...]:
        """
        Получает список всех записей из таблицы `weapon_list` базы данных.
        :return: Список списков, где каждый внутренний список содержит идентификатор страницы и URL оружия.
                 Формат: [[page_id, url], ...]
        """
        with self.conn:
            cursor = self.conn.cursor()
            query = cursor.execute('SELECT * FROM weapon_list').fetchall()
            result = [[i[1], i[2]] for i in query]
            return result

    def delete_from_weapon_list(self, page_id) -> None:
        """
        Удаляет запись из таблицы `weapon_list` базы данных по идентификатору страницы.
        :param page_id: str Идентификатор страницы для удаления.
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM weapon_list WHERE page_id = ?', (page_id,))
