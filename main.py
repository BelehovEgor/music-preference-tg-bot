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

GO_BACK = "back_page"
GO_NEXT = "next_page"

TRACK = "track"
PLAYLIST = "playlist"


# Функция для добавления навигации
def create_navigation(current_page, pages_count, keyboard, next_text, back_text):
    # Добавим номер страницы и кнопки вперед/назад
    # Если у нас всего 1 страница (может быть 0 аудио)
    if pages_count == 0 or pages_count == 1:
        back_button = types.InlineKeyboardButton("◀️", callback_data="inactive")
        next_button = types.InlineKeyboardButton("▶️", callback_data="inactive")
        number_package_page = types.InlineKeyboardButton(f"{1}/{1}",
                                                         callback_data="number_page")

    # Если страниц больше, чем 1
    else:
        back_button = types.InlineKeyboardButton("◀️", callback_data=f"{back_text}")
        next_button = types.InlineKeyboardButton("▶️", callback_data=f"{next_text}")
        number_package_page = types.InlineKeyboardButton(f"{current_page + 1}/{pages_count}",
                                                         callback_data="number_page")

    keyboard.row(back_button, number_package_page, next_button)


def create_songs_page(user_id, current_page):
    # Количество записей на одной странице
    record_on_page = 8

    songs, total_page_count = service.get_songs(user_id, current_page, record_on_page)

    page_text = "👇Список треков👇"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for song in songs:
        song_id = song[0]
        song_name = song[1]

        # Присвоим имя кнопке для обработки ее нажатия
        button_callback_data = TRACK + "_" + str(song_id)
        button = types.InlineKeyboardButton(song_name, callback_data=button_callback_data)

        keyboard.add(button)

    # Добавим навигацию
    create_navigation(current_page, total_page_count, keyboard, "next_page", "back_page")

    # Создадим страницу со списком треков
    message_id = service.get_bot_message_id(user_id)
    bot.edit_message_text(chat_id=user_id, text=page_text, message_id=message_id, reply_markup=keyboard,
                          parse_mode='html')


# TODO
def create_playlists_page(user_id, current_page):
    xx = 0


def process_add_track(user_id):
    service.set_start_song_draft(user_id, True)

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


def process_tracks(user_id, resend):
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

    service.set_start_song_draft(user_id, False)

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
    def start(message):
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
                    process_tracks(user_id, False)

                # TODO
                elif call.data == PLAYLISTS:
                    xx = 0

                elif call.data == ADD_TRACK:
                    process_add_track(user_id)

                elif call.data == GET_TRACKS_LIST:
                    service.set_current_page(user_id, 0, TRACKS)
                    create_songs_page(user_id, 0)

                elif call.data == GO_BACK or call.data == GO_NEXT:
                    previous_page, page_type = service.get_current_page(user_id)

                    # Выберем направление перемещения(+1 -> следующая, -1 -> предыдущая)
                    next_back_index = 1 if call.data == GO_NEXT else -1

                    current_page = previous_page + next_back_index

                    # Вычислим корректный номер текущей страницы
                    total_page_count = service.get_total_page_tracks(user_id)
                    if current_page < 0:
                        current_page = total_page_count - 1
                    elif current_page > total_page_count - 1:
                        current_page = 0

                    service.set_current_page(user_id, current_page, page_type)

                    # Если мы сейчас листаем страницы Треков
                    if page_type == TRACKS:
                        # Вышлем следующую/предыдущую страницу
                        create_songs_page(user_id, current_page)

                    # Если мы сейчас листаем страницы Плейлистов
                    elif page_type == PLAYLISTS:
                        # Вышлем следующую/предыдущую страницу
                        create_playlists_page(user_id, current_page)

                # TODO
                elif call.data.split("_")[0] == TRACK:
                    track_id = int(call.data.split("_")[1])
                    xx = 0

                # TODO
                elif call.data.split("_")[0] == PLAYLIST:
                    playlist_id = int(call.data.split("_")[1])

                # TODO - чет еще
                else:
                    xx = 0

        except Exception as e:
            print(repr(e))


    # Обработка сообщения после ввода текста пользователем
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

                        process_tracks(user_id, True)

            except Exception as e:
                print(repr(e))


    bot.polling()
