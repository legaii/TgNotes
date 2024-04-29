class Item:
    def __init__(self, text: str, deleted: bool):
        self.text = text
        self.deleted = deleted

    @classmethod
    def from_json(cls, document: dict):
        return cls(document['text'], document['deleted'])

    def to_json(self) -> dict:
        return {'text': self.text, 'deleted': self.deleted}

    def get_text(self, max_len: int = 25) -> str:
        return (
            self.text if len(self.text) <= max_len
            else self.text[:max_len - 3] + '...'
        ).replace('\n', ' ')
