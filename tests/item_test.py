from unittest import TestCase
from src.item import Item


class ItemTest(TestCase):
    def setUp(self):
        self.item = Item('abacaba', True)

    def test_json(self):
        new_item = Item.from_json(self.item.to_json())
        self.assertEqual(new_item.text, self.item.text)
        self.assertEqual(new_item.deleted, self.item.deleted)

    def test_get_text(self):
        self.assertEqual(self.item.get_text(5), 'ab...')
