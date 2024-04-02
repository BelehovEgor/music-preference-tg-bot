import telebot
from telebot import types

import config
import service

START = "start"
MENU = "menu"
TRACKS = "tracks"
PLAYLISTS = "playlists"
HELP = "help"
ADD_TRACK = "add_track"
GET_TRACKS_LIST = "get_tracks_list"


def create_tracks_menu(user_id, resend):
    page_text = "Выберите кнопку"
    message_id = service.get_bot_message_id(user_id)

    # Создаем Inline клавиатуру для главного меню
    keyboard = types.InlineKeyboardMarkup()
    add_track = types.InlineKeyboardButton("Добавить трек", callback_data=ADD_TRACK)
    get_tracks_list = types.InlineKeyboardButton("Список треков", callback_data=GET_TRACKS_LIST)
    keyboard.add(add_track)
    keyboard.add(get_tracks_list)

    if resend:
        message = bot.send_message(chat_id=user_id, text=page_text, reply_markup=keyboard, parse_mode='html')
        service.set_bot_message_id(user_id, message.id)
    else:
        # Бот изменяет сообщение на новую страницу
        bot.edit_message_text(chat_id=user_id, text=page_text,
                              message_id=message_id,
                              reply_markup=keyboard, parse_mode='html')


# Функция для создания страницы с главным меню
def create_menu_page(user_id):
    # Текст главного меню
    menu_text = "\n\n👇 ГЛАВНОЕ МЕНЮ 👇"

    # Удаляем Inline клавиатуру, если она осталась
    message_id = service.get_bot_message_id(user_id)
    if message_id is not None:
        # Если пользователь удалил переписку, то возможно ничего удалять и не надо
        try:
            bot.delete_message(chat_id=user_id, message_id=message_id)
        except Exception as e:
            print(repr(e))

    # Создаем Inline клавиатуру для главного меню
    markup = types.InlineKeyboardMarkup(row_width=2)
    package = types.InlineKeyboardButton("Треки", callback_data=TRACKS)
    catalog = types.InlineKeyboardButton("Плейлисты", callback_data=PLAYLISTS)
    help_item = types.InlineKeyboardButton("Помощь", callback_data=HELP)
    markup.add(package)
    markup.add(catalog)
    markup.add(help_item)

    # Добавляем Inline клавиатуру в главном меню
    message = bot.send_message(user_id, menu_text, parse_mode='html', reply_markup=markup)
    service.set_bot_message_id(user_id, message.id)


if __name__ == '__main__':
    # Подключение к API телеграм с помощью токена бота
    bot = telebot.TeleBot(config.TOKEN)


    # Обработка команды /start или /menu
    @bot.message_handler(commands=[START, MENU])
    def start(message) -> None:
        user_id = message.from_user.id

        # Отсылаем стартовое сообщение
        create_menu_page(user_id)


    # Обработка команды /help
    @bot.message_handler(commands=[HELP])
    def handle_start(message):
        user_id = message.from_user.id


    # Обработка нажатия на кнопки
    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        try:
            if call.message:
                user_id = call.from_user.id

                if call.data == TRACKS:
                    create_tracks_menu(user_id, False)

                elif call.data == PLAYLISTS:
                    # Обновим поле текущей страницы
                    xx = 0

                elif call.data == ADD_TRACK:
                    service.start_song_draft(user_id)

                    # Удаляем Inline клавиатуру, если она осталась
                    message_id = service.get_bot_message_id(user_id)
                    if message_id is not None:
                        # Если пользователь удалил переписку, то возможно ничего удалять и не надо
                        try:
                            bot.delete_message(chat_id=user_id, message_id=message_id)
                        except Exception as e:
                            print(repr(e))

                    text = "Введите ссылку"
                    bot.send_message(user_id, text, parse_mode='html')

                elif call.data == GET_TRACKS_LIST:
                    xx = 0

                else:
                    xx = 0

        except Exception as e:
            print(repr(e))


    # TODO - Обработка сообщения после ввода текста пользователем
    @bot.message_handler(content_types=['text'])
    def message_from_bot(message):
        if message.chat.type == "private":
            user_id = message.from_user.id

            try:
                if service.is_user_starting_draft(user_id):
                    song_link, song_performer, song_name = service.get_user_song_draft(user_id)
                    if song_link is None:
                        service.set_draft_song_link(user_id, message.text)
                        text = "Введите автора"
                        bot.send_message(user_id, text, parse_mode='html')
                    elif song_performer is None:
                        service.set_draft_song_performer(user_id, message.text)
                        text = "Введите имя трека"
                        bot.send_message(user_id, text, parse_mode='html')
                    elif song_name is None:
                        service.set_draft_song_name(user_id, message.text)
                        service.create_song(user_id)

                        create_tracks_menu(user_id, True)

            except Exception as e:
                print(repr(e))


    bot.polling()
