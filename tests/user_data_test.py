from unittest import TestCase
from src.user_data import UserData


class UserDataTest(TestCase):
    ITEMS_CNT = 100

    def setUp(self):
        self.user_data = UserData()
        for i in range(self.ITEMS_CNT):
            self.user_data.add_item(str(i))

    def test_json(self):
        new_user_data = UserData.from_json(self.user_data.to_json())
        for new_item, item in zip(new_user_data.items, self.user_data.items):
            self.assertEqual(new_item.text, item.text)

    def test_add_item(self):
        self.user_data.add_item('abacaba')
        self.assertEqual(self.user_data.pages_cnt(), 11)

    def test_delete_item(self):
        for _ in range(3):
            for _ in range(self.ITEMS_CNT):
                self.user_data.prev_page()
            for _ in range(self.ITEMS_CNT):
                self.user_data.next_page()
        self.user_data.delete_item(42)
        self.assertEqual(self.user_data.pages_cnt(), 10)
        for i in range(10):
            self.user_data.delete_item(self.ITEMS_CNT - i - 1)
        self.assertEqual(self.user_data.pages_cnt(), 9)

    def test_main_message_text(self):
        self.assertEqual(UserData().get_main_message_text(), 'Пусто')
        self.assertEqual(
            self.user_data.get_main_message_text(),
            'Страница 1 из 10\n\n' + '\n\n'.join(f'/{i}\n{i}' for i in range(10))
        )
