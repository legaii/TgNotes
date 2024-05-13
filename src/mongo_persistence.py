from telegram.ext import BasePersistence
from pymongo.database import Database
from .user_data import UserData


class MongoPersistence(BasePersistence):
    """Класс для чтения и записи UserData и информации от ConversationHandler в базу данных"""

    def __init__(self, mongo_db: Database):
        super().__init__()
        self.mongo_db = mongo_db

    async def get_bot_data(self) -> dict:
        return dict()

    async def update_bot_data(self, data: dict) -> None:
        pass

    async def refresh_bot_data(self, bot_data: dict) -> None:
        pass

    async def get_chat_data(self) -> dict:
        return dict()

    async def update_chat_data(self, chat_id: int, data: dict) -> None:
        pass

    async def refresh_chat_data(self, chat_id: int, chat_data: dict) -> None:
        pass

    async def drop_chat_data(self, chat_id: int) -> None:
        pass

    async def get_user_data(self) -> dict:
        """Возвращает UserData для всех пользователей (в виде словаря с ключами user_id)"""
        return {
            document['user_id']: UserData.from_json(document['user_data'])
            for document in self.mongo_db.user_data.find()
        }

    async def update_user_data(self, user_id: int, data: UserData) -> None:
        """Изменяет в базе данных UserData для пользователя user_id"""
        self.mongo_db.user_data.update_one(
            {'user_id': user_id}, {'$set': {'user_data': data.to_json()}}, upsert=True
        )

    async def refresh_user_data(self, user_id: int, user_data: UserData) -> None:
        pass

    async def drop_user_data(self, user_id: int) -> None:
        """Удаляет в базе данных UserData для пользователя user_id"""
        self.mongo_db.user_data.delete_one({'user_id': user_id})

    async def get_callback_data(self) -> None:
        pass

    async def update_callback_data(self, data: dict) -> None:
        pass

    async def get_conversations(self, name: str) -> dict:
        """Возвращает информацию для ConversationHandler с именем name"""
        return {
            tuple(document['key']): document['state']
            for document in self.mongo_db[name].find()
        }

    async def update_conversation(self, name: str, key: tuple, new_state: int) -> None:
        """Изменяет информацию с ключом key для ConversationHandler с именем name"""
        self.mongo_db[name].update_one(
            {'key': list(key)}, {'$set': {'state': new_state}}, upsert=True
        )

    async def flush(self) -> None:
        pass
