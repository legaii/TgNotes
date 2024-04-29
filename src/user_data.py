from item import Item


class UserData:
    PAGE_SIZE = 10

    def __init__(self):
        self.main_message_id = None
        self.current_page = 0
        self.current_item_id = None
        self.items = []

    @classmethod
    def from_json(cls, document: dict):
        self = cls()
        self.main_message_id = document['main_message_id']
        self.current_page = document['current_page']
        self.current_item_id = document['current_item_id']
        self.items = [Item.from_json(item) for item in document['items']]
        return self

    def to_json(self) -> dict:
        return {
            'main_message_id': self.main_message_id,
            'current_page': self.current_page,
            'current_item_id': self.current_item_id,
            'items': [item.to_json() for item in self.items]
        }

    def pages_cnt(self) -> int:
        return (
            len([item for item in self.items if not item.deleted]) + self.PAGE_SIZE - 1
        ) // self.PAGE_SIZE

    def add_item(self, text: str) -> None:
        self.items.append(Item(text, False))

    def delete_item(self, item_id: int) -> None:
        self.items[item_id].deleted = True
        if self.current_page > 0 and self.current_page >= self.pages_cnt():
            self.current_page -= 1

    def next_page(self) -> None:
        if self.current_page + 1 < self.pages_cnt():
            self.current_page += 1

    def prev_page(self) -> None:
        if self.current_page > 0:
            self.current_page -= 1

    def get_main_message_text(self) -> str:
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
