from telegram.ext import Application, ApplicationBuilder
from pymongo import MongoClient
from .mongo_persistence import MongoPersistence
from .handlers import Context, main_handlers
from .telegram_token import TOKEN


if __name__ == '__main__':
    mongo_client = MongoClient()
    async def post_shutdown(app: Application) -> None:
        """Функция, закрывающая соединение с базой данных"""
        mongo_client.close()


    persistence = MongoPersistence(mongo_client.mongo_db)
    app = (ApplicationBuilder()
        .concurrent_updates(False)
        .context_types(Context)
        .persistence(persistence)
        .token(TOKEN)
        .post_shutdown(post_shutdown)
    ).build()

    for handler in main_handlers:
        app.add_handler(handler)
    app.run_polling()
