from item import Item


class UserData:
    def __init__(self):
        self.main_message_id = None
        self.current_item_id = None
        self.items = []

    @classmethod
    def from_json(cls, document: dict):
        self = cls()
        self.main_message_id = document['main_message_id']
        self.current_item_id = document['current_item_id']
        self.items = [Item.from_json(item) for item in document['items']]
        return self

    def to_json(self) -> dict:
        return {
            'main_message_id': self.main_message_id,
            'current_item_id': self.current_item_id,
            'items': [item.to_json() for item in self.items]
        }

    def get_main_message_text(self) -> str:
        items_text = []
        for item_id, item in enumerate(self.items):
            if not item.deleted:
                items_text.append(f'/{item_id}\n' + item.get_text())
        return '\n\n'.join(items_text) if len(items_text) > 0 else 'Пусто'
