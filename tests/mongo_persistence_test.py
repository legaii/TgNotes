from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from src.mongo_persistence import MongoPersistence
from src.user_data import UserData


class MongoPersistenceTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mongo_db_mock = MagicMock()
        self.persistence = MongoPersistence(self.mongo_db_mock)

    async def test_user_data(self):
        user_data = UserData()
        user_data_json = {'user_data': user_data.to_json()}
        user_id_json = {'user_id': 0}
        self.mongo_db_mock.user_data.find.return_value=[user_id_json | user_data_json]

        await self.persistence.update_user_data(0, user_data)
        self.mongo_db_mock.user_data.update_one.assert_called_once_with(
            user_id_json, {'$set': user_data_json}, upsert=True
        )

        self.assertIsNone(await self.persistence.refresh_user_data(0, user_data))

        all_data = await self.persistence.get_user_data()
        self.mongo_db_mock.user_data.find.assert_called_once_with()
        self.assertEqual(len(all_data), 1)
        self.assertTrue(0 in all_data)
        self.assertEqual(all_data[0].to_json(), user_data.to_json())

        await self.persistence.drop_user_data(0)
        self.mongo_db_mock.user_data.delete_one.assert_called_once_with(user_id_json)

    async def test_conversations(self):
        key_json = {'key': [1, 2]}
        state_json = {'state': 3}
        self.mongo_db_mock['a'].find.return_value=[key_json | state_json]

        await self.persistence.update_conversation('a', (1, 2), 3)
        self.mongo_db_mock['a'].update_one.assert_called_once_with(
            key_json, {'$set': state_json}, upsert=True
        )

        conversations = await self.persistence.get_conversations('a')
        self.mongo_db_mock['a'].find.assert_called_once_with()
        self.assertEqual(conversations, {(1, 2): 3})

    async def test_trivial_methods(self):
        self.assertEqual(await self.persistence.get_bot_data(), dict())
        self.assertIsNone(await self.persistence.update_bot_data(dict()))
        self.assertIsNone(await self.persistence.refresh_bot_data(dict()))
        self.assertEqual(await self.persistence.get_chat_data(), dict())
        self.assertIsNone(await self.persistence.update_chat_data(0, dict()))
        self.assertIsNone(await self.persistence.refresh_chat_data(0, dict()))
        self.assertIsNone(await self.persistence.drop_chat_data(0))
        self.assertIsNone(await self.persistence.get_callback_data())
        self.assertIsNone(await self.persistence.update_callback_data(tuple()))
        self.assertIsNone(await self.persistence.flush())
        self.persistence.mongo_db.assert_not_called()
