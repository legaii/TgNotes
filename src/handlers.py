from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, CommandHandler, ConversationHandler, ContextTypes
import telegram.ext.filters as filters

from user_data import UserData
from item import Item


ADDING, EDITING = range(2)
Context = ContextTypes(user_data=UserData)


def get_help_text() -> str:
    with open('assets/help.txt') as help_file:
        return help_file.read()


async def item_not_found_error(update: Update, context: Context.context) -> int:
    await update.message.reply_text('Карточка не найдена')
    return ConversationHandler.END


async def unknown_command_error(update: Update, context: Context.context) -> int:
    await update.message.reply_text('Неизвестная команда')
    return ConversationHandler.END


async def help_callback(update: Update, context: Context.context) -> int:
    context.user_data.current_item_id = None
    await update.message.reply_text(get_help_text())
    return ConversationHandler.END


async def cancel_callback(update: Update, context: Context.context) -> int:
    context.user_data.current_item_id = None
    await update.message.reply_text('Операция успешно отменена')
    return ConversationHandler.END


async def delete_main_message(update: Update, context: Context.context) -> None:
    msg_id = context.user_data.main_message_id
    if msg_id is not None:
        await context.bot.delete_message(chat_id=update.message.chat.id, message_id=msg_id)
        context.user_data.main_message_id = None


async def update_main_message(update: Update, context: Context.context) -> None:
    msg_id = context.user_data.main_message_id
    if msg_id is not None:
        await context.bot.edit_message_text(
            context.user_data.get_main_message_text(),
            chat_id=update.message.chat.id,
            message_id=msg_id
        )


async def get_all_callback(update: Update, context: Context.context) -> int:
    context.user_data.current_item_id = None
    await delete_main_message(update, context)
    message = await update.message.reply_text(context.user_data.get_main_message_text())
    context.user_data.main_message_id = message.message_id
    return ConversationHandler.END


async def get_item_callback(update: Update, context: Context.context) -> int:
    item_id = int(context.matches[0].group(1))
    context.user_data.current_item_id = item_id
    items = context.user_data.items
    if item_id >= len(items):
        return await item_not_found_error(update, context)
    await update.message.reply_text(items[item_id].text)
    await update.message.reply_text('Редактировать: /edit\nУдалить: /delete')
    return ConversationHandler.END


async def init_add_callback(update: Update, context: Context.context) -> int:
    context.user_data.current_item_id = None
    await update.message.reply_text('Введите текст:')
    return ADDING


async def add_item_callback(update: Update, context: Context.context) -> int:
    context.user_data.items.append(Item(update.message.text, False))
    await update_main_message(update, context)
    await update.message.reply_text('Готово!')
    return ConversationHandler.END


async def init_edit_callback(update: Update, context: Context.context) -> int:
    if context.user_data.current_item_id is None:
        return await item_not_found_error(update, context)
    await update.message.reply_text('Введите новый текст:')
    return EDITING


async def edit_item_callback(update: Update, context: Context.context) -> int:
    item_id = context.user_data.current_item_id
    if item_id is None:
        return await item_not_found_error(update, context)
    context.user_data.items[item_id].text = update.message.text
    context.user_data.current_item_id = None
    await update_main_message(update, context)
    await update.message.reply_text('Готово!')
    return ConversationHandler.END


async def delete_item_callback(update: Update, context: Context.context) -> int:
    item_id = context.user_data.current_item_id
    if item_id is None:
        return await item_not_found_error(update, context)
    context.user_data.items[item_id].deleted = True
    context.user_data.current_item_id = None
    await update_main_message(update, context)
    await update.message.reply_text('Готово!')
    return ConversationHandler.END


help_handler = CommandHandler(['start', 'help'], help_callback)
cancel_handler = CommandHandler('cancel', cancel_callback)
get_all_handler = CommandHandler('all', get_all_callback)
get_item_handler = MessageHandler(filters.Regex(r'^/(\d+)$'), get_item_callback)
init_add_handler = CommandHandler('add', init_add_callback)
add_item_handler = MessageHandler(filters.TEXT, add_item_callback)
init_edit_handler = CommandHandler('edit', init_edit_callback)
edit_item_handler = MessageHandler(filters.TEXT, edit_item_callback)
delete_item_handler = CommandHandler('delete', delete_item_callback)

default_handlers = [
    help_handler,
    cancel_handler,
    get_all_handler,
    get_item_handler,
    init_add_handler,
    init_edit_handler,
    delete_item_handler,
    unknown_command_error,
]

main_handler = ConversationHandler(
    default_handlers,
    {
        ADDING: [help_handler, cancel_handler, add_item_handler],
        EDITING: [help_handler, cancel_handler, edit_item_handler]
    },
    default_handlers,
    name='main_conversation', persistent=True
)
