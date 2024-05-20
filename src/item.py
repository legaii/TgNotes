class Item:
    """Класс для хранения всей информации о карточке"""

    def __init__(self, text: str, deleted: bool):
        self.text = text
        self.deleted = deleted

    @classmethod
    def from_json(cls, document: dict):
        """Конструирует новый объект Item из json-объекта"""
        return cls(document['text'], document['deleted'])

    def to_json(self) -> dict:
        """Возвращает json-представление данного объекта"""
        return {'text': self.text, 'deleted': self.deleted}

    def get_text(self, max_len: int = 25) -> str:
        """Возвращает текст карточки, обрезанный так, чтобы его длина не превышала max_len"""
        return (
            self.text if len(self.text) <= max_len
            else self.text[:max_len - 3] + '...'
        ).replace('\n', ' ')
