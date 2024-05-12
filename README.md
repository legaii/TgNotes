# TgNotes

### Описание проекта
Telegram-бот для ведения текстовых заметок.

### Как запустить?
##### Создаем бота:
* Создаем telegram-бота через [@BotFather](https://t.me/botfather). Пусть вам дали токен ```XXX```
* ```echo 'TOKEN = "XXX"' > src/telegram_token.py```
##### Запускаем базу данных:
* ```docker pull mongodb/mongodb-community-server:latest```
* ```docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest```
##### Далее запускаем самого бота:
* ```pip3 install -r requirements.txt```
* ```python3 src/main.py```

### Стек технологий
* [Python](https://www.python.org/)
* Библиотека [python-telegram-bot](https://python-telegram-bot.org/)
* База данных [MongoDB](https://www.mongodb.com/) и библиотека [PyMongo](https://pymongo.readthedocs.io/en/stable/)

### Реализуемый функционал
##### Основные сущности
* **Карточка**. Это обычная текстовая заметка. У каждой карточки есть номер.
##### Доступные команды
* ```/start``` и ```/help``` - показать список команд.
* ```/cancel``` - отменить текущую операцию.
* ```/all``` - перечислить все карточки. Бот присылает список из первых 10 карточек, остальные карточки находятся на следующих "страницах". Пользователь может перемещаться по "страницам" с помощью [inline keyboard](https://core.telegram.org/bots/features#inline-keyboards). Рядом с каждой карточкой будет команда вида ```/n```, нажав на которую пользователь может открыть эту карточку.
* ```/n``` - открыть карточку с номером ```n```.
* ```/edit``` - редактировать текст текущей карточки.
* ```/delete``` - удалить текущую карточку.
* ```/add``` - добавить новую карточку
* Примечание: пользователю никогда не придется вручную вводить номера карточек, он просто будет нажимать на кликабельные команды в сообщениях бота.

### Архитектура
##### Список классов:
* ```class Item:```
  * Это карточка.
  * Атрибуты:
    * ```text: str```
    * ```deleted: bool```
  * Методы:
    * ```get_text(max_len: int) -> str``` - возвращает ```text```, обрезанный так, чтобы его длина была не больше ```max_len```, и он заканчивался на ```...``` (чтобы красиво отображать начало карточки в результате выполнения команды ```/all```).
    * ```staticmethod from_json(document: dict) -> Item``` - создает объект ```Item``` из словаря вида ```{'text': 'abacaba', 'deleted': False}```.
    * ```to_json() -> dict``` - возвращает словарь вышеописанного вида.

* ```class UserData```
  * Атрибуты:
    * ```main_message_id: int``` - id сообщения, в котором на данный момент показывается список карточек (это нужно, чтобы иметь возможность редактировать это сообщение при перелистывании "страниц").
    * ```current_item_id: int``` - номер текущей карточки.
    * ```items: List[Item]``` - список карточек (в том числе удаленных).
  * Методы:
    * ```get_main_message_text() -> str``` - возвращает полный текст сообщения для результата выполнения команды ```/all```.
    * ```staticmethod from_json(document: dict) -> UserData``` - создает объект ```UserData``` из словаря вида ```{'main_message_id': 1, 'current_item_id': 2, 'items': [{'text': 'abacaba', 'deleted': False}]}```.
    * ```to_json() -> dict``` - возвращает словарь вышеописанного вида.

* ```class Persistence(telegram.ext.BasePersistence):```
  * Класс для доступа к базе данных
  * Атрибуты:
    * ```mongo_db: pymongo.database.Database```
  * Методы:
    * ```get_user_data() -> Dict[int, UserData]``` - возвращает ```UserData``` для всех пользователей.
    * ```update_user_data(user_id: int, data: UserData) -> None``` - обновляет в базе данный ```UserData``` для пользователя ```user_id```.
    * ```get_conversations(name: str) -> dict``` - возвращает объект, который необходим для ```telegram.ext.ConversationHandler```. Это нужно, чтобы бот запоминал, на чем закончился диалог с пользователем, если сервер по какой-то причине упал.
    * ```update_conversations(name: str, key: tuple, new_state: int) -> None``` - записывает в базу данных данные для ```telegram.ext.ConversationHandler```.
    * Много других методов, которые нужно как-то (неважно как) переопределить. Список методов указан [здесь](https://docs.python-telegram-bot.org/en/v21.1.1/telegram.ext.basepersistence.html).

* ```class Handlers:```
  * Класс, который просто содержит все необходимые [обработчики](https://docs.python-telegram-bot.org/en/v21.1.1/telegram.ext.handlers-tree.html) команд.
  * ```help_handler: CommandHandler``` - обработчик команд ```/start``` и ```/help```.
  * ```cancel_handler: CommandHandler``` - обработчик команды ```/cancel```.
  * ```get_all_handler: CommandHandler``` - обработчик команды ```/all```.
  * ```get_item_handler: CommandHandler``` - обработчик команд вида ```/n```.
  * ```init_add_handler: CommandHandler``` - обработчик команды ```/add```. Переводит бота в состояние ```ADDING```, в котором он ждет текста для создания новой карточки.
  * ```add_item_handler: MessageHandler``` - обработчик сообщений в состоянии ```ADDING```.
  * ```init_edit_handler: CommandHandler``` - обработчик команды ```/edit```. Переводит бота в состояние ```EDITING```, в котором он ждет нового текста для редактирования старой карточки.
  * ```edit_item_handler: MessageHandler``` - обработчик сообщений в состоянии ```EDITING```.
  * ```delete_item_handler: CommandHandler``` - обработчик команды ```/delete```.
  * ```main_handler: ConversationHandler``` - обработчик, который хранит в себе все вышеописанные обработчики и текущее состояние диалога со всеми пользователями.
