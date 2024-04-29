from telegram.ext import Application, ApplicationBuilder
from pymongo import MongoClient
from mongo_persistence import MongoPersistence
from handlers import Context, main_handler
from telegram_token import TOKEN


if __name__ == '__main__':
    mongo_client = MongoClient()
    async def post_shutdown(app: Application) -> None:
        mongo_client.close()


    persistence = MongoPersistence(mongo_client.mongo_db)
    app = (ApplicationBuilder()
        .concurrent_updates(False)
        .context_types(Context)
        .persistence(persistence)
        .token(TOKEN)
        .post_shutdown(post_shutdown)
    ).build()

    app.add_handler(main_handler)
    app.run_polling()
