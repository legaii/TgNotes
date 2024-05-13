from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock, call
from telegram.error import BadRequest
from src.user_data import UserData
from src.handlers import (
    KEYBOARD,
    Context,
    get_help_text,
    help_callback,
    cancel_callback,
    get_all_callback,
    get_item_callback,
    init_add_callback,
    add_item_callback,
    init_edit_callback,
    edit_item_callback,
    delete_item_callback,
    next_page_callback,
    prev_page_callback,
    unknown_command_error,
)


class HandlersTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.update = MagicMock()
        self.update.message.text = 'text'
        self.update.message.reply_text = AsyncMock()
        self.context = MagicMock()
        self.context.user_data = UserData()
        self.context.user_data.main_message_id = 0
        self.context.user_data.add_item('abacaba')
        self.context.bot.delete_message = AsyncMock()
        self.context.bot.edit_message_text = self.edit_message_text
        self.msg_text = self.context.user_data.get_main_message_text()

    async def edit_message_text(self, new_text, **kwargs):
        if new_text == self.msg_text:
            raise BadRequest('The new text is a copy of the old one')
        self.msg_text = new_text

    async def test_help(self):
        await help_callback(self.update, self.context)
        self.update.message.reply_text.assert_awaited_once_with(get_help_text())

    async def test_cancel(self):
        await cancel_callback(self.update, self.context)
        self.update.message.reply_text.assert_awaited_once_with('Операция успешно отменена')

    async def test_get_all(self):
        await get_all_callback(self.update, self.context)
        self.update.message.reply_text.assert_awaited_once_with(
            self.context.user_data.get_main_message_text(), reply_markup=KEYBOARD
        )

    async def test_get_item(self):
        self.context.matches[0].group.return_value = '0'
        await get_item_callback(self.update, self.context)
        self.update.message.reply_text.assert_has_awaits([call('abacaba')])

    async def test_item_not_found(self):
        self.context.matches[0].group.return_value = '1'
        await get_item_callback(self.update, self.context)
        self.update.message.reply_text.assert_awaited_once_with('Карточка не найдена')

    async def test_init_add(self):
        await init_add_callback(self.update, self.context)
        self.update.message.reply_text.assert_awaited_once_with('Введите текст:')

    async def test_add_item(self):
        await add_item_callback(self.update, self.context)
        self.update.message.reply_text.assert_awaited_once_with('Готово!')
        self.assertEqual(len(self.context.user_data.items), 2)
        self.assertEqual(self.context.user_data.items[1].get_text(), 'text')

    async def test_init_edit(self):
        for item_id in (0, None):
            self.context.user_data.current_item_id = item_id
            await init_edit_callback(self.update, self.context)
            self.update.message.reply_text.assert_awaited_with(
                'Введите новый текст:' if item_id == 0 else 'Карточка не найдена'
            )

    async def test_edit_item(self):
        for item_id in (0, None):
            self.context.user_data.current_item_id = item_id
            await edit_item_callback(self.update, self.context)
            self.update.message.reply_text.assert_awaited_with(
                'Готово!' if item_id == 0 else 'Карточка не найдена'
            )
            if item_id == 0:
                self.assertEqual(len(self.context.user_data.items), 1)
                self.assertEqual(self.context.user_data.items[0].get_text(), 'text')

    async def test_delete_item(self):
        for item_id in (0, None):
            self.context.user_data.current_item_id = item_id
            await delete_item_callback(self.update, self.context)
            self.update.message.reply_text.assert_awaited_with(
                'Готово!' if item_id == 0 else 'Карточка не найдена'
            )
            if item_id == 0:
                self.assertIsNone(self.context.user_data.current_item_id)
                self.assertEqual(self.context.user_data.get_main_message_text(), 'Пусто')

    async def test_next_prev_page(self):
        for i in range(10):
            self.context.user_data.add_item(str(i))
        self.msg_text = self.context.user_data.get_main_message_text()
        await prev_page_callback(self.update, self.context)
        self.assertTrue(self.msg_text.startswith('Страница 1'))
        await next_page_callback(self.update, self.context)
        self.assertTrue(self.msg_text.startswith('Страница 2'))
        await prev_page_callback(self.update, self.context)
        self.assertTrue(self.msg_text.startswith('Страница 1'))

    async def test_unknown_command(self):
        await unknown_command_error(self.update, self.context)
        self.update.message.reply_text.assert_awaited_once_with('Неизвестная команда')
