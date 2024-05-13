from .item import Item


class UserData:
    """Класс для хранения всей информации об одном пользователе"""
    PAGE_SIZE = 10

    def __init__(self):
        self.main_message_id = None
        self.current_page = 0
        self.current_item_id = None
        self.items = []

    @classmethod
    def from_json(cls, document: dict):
        """Конструирует новый объект UserData из json-объекта"""
        self = cls()
        self.main_message_id = document['main_message_id']
        self.current_page = document['current_page']
        self.current_item_id = document['current_item_id']
        self.items = [Item.from_json(item) for item in document['items']]
        return self

    def to_json(self) -> dict:
        """Возвращает json-представление данного объекта"""
        return {
            'main_message_id': self.main_message_id,
            'current_page': self.current_page,
            'current_item_id': self.current_item_id,
            'items': [item.to_json() for item in self.items]
        }

    def pages_cnt(self) -> int:
        """Возвращает количество страниц, необходимое для перечисления всех неудаленных карточек"""
        return (
            len([item for item in self.items if not item.deleted]) + self.PAGE_SIZE - 1
        ) // self.PAGE_SIZE

    def add_item(self, text: str) -> None:
        """Добавляет новую карточку с текстом text"""
        self.items.append(Item(text, False))

    def delete_item(self, item_id: int) -> None:
        """Удаляет карточку с номером item_id"""
        self.items[item_id].deleted = True
        if self.current_page > 0 and self.current_page >= self.pages_cnt():
            self.current_page -= 1

    def next_page(self) -> None:
        """Перелистывает список всех неудаленных карточек на следующую страницу"""
        if self.current_page + 1 < self.pages_cnt():
            self.current_page += 1

    def prev_page(self) -> None:
        """Перелистывает список всех неудаленных карточек на предыдущую страницу"""
        if self.current_page > 0:
            self.current_page -= 1

    def get_main_message_text(self) -> str:
        """Возвращает текст текущей страницы списка всех неудаленных карточек"""
        items_text = []
        for item_id, item in enumerate(self.items):
            if not item.deleted:
                items_text.append(f'/{item_id}\n' + item.get_text())
        page_text = '\n\n'.join(
            items_text[
                self.current_page * self.PAGE_SIZE :
                (self.current_page + 1) * self.PAGE_SIZE
            ]
        )
        if len(page_text) == 0:
            return 'Пусто'
        return f'Страница {self.current_page + 1} из {self.pages_cnt()}\n\n{page_text}'
