from typing import Type

import sqlalchemy
import telebot
from telebot import types
from re import match, search

import config
import services
from models import Base, SongDraft

import service2

START = "start"
MENU = "menu"
TRACKS = "tracks"
PLAYLISTS = "playlists"
HELP = "help"
ADD_TRACK = "add_track"
GET_TRACKS_LIST = "get_tracks_list"

BACK_PAGE = "back_page"
NEXT_PAGE = "next_page"

TRACK = "track"
PLAYLIST = "playlist"

ADD_PLAYLIST = "add_playlist"
GET_PLAYLISTS_LIST = "get_playlists_list"

CHANGE_TRACK = "change_track"
DELETE_TRACK = "delete_track"

GO_BACK = "go_back"

ADD_TRACK_TO_PLAYLIST = "add_track_to_playlist"
ADD_MEMBER = "add_member"
DELETE_PLAYLIST = "delete_playlist"

END_CHANGE_PLAYLIST = "end_change_playlist"


def send_song_info_message(user_id, track_id):
    song_name, song_performer, song_link = service.get_song(track_id)
    track_info = f"👇\n• Название: {song_name}\n• Исполнитель: {song_performer}\n• Ссылка: {song_link}"

    keyboard = types.InlineKeyboardMarkup()
    change_track = types.InlineKeyboardButton("Редактировать", callback_data=CHANGE_TRACK)
    delete_track = types.InlineKeyboardButton("Удалить", callback_data=f"DELETE_TRACK_{track_id}")
    keyboard.row(change_track, delete_track)

    # Создадим страницу с информацией по треку
    message_id = service.get_bot_message_id(user_id)
    bot.edit_message_text(chat_id=user_id, text=track_info, message_id=message_id, reply_markup=keyboard,
                          parse_mode='html')


def add_track_to_playlist(user_id, track_id):
    playlist_id = service2.get_playlist_id(user_id)
    service2.save_song_to_playlist(track_id, playlist_id)
    song_name, song_performer, song_link = service.get_song(track_id)
    track_info = f"Трек успешно добавлен:\n• Название: {song_name}\n• Исполнитель: {song_performer}\n• Ссылка: {song_link}"

    # Создадим страницу с информацией по треку
    bot.send_message(chat_id=user_id, text=track_info, parse_mode='html')


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
    playlist_id = service2.get_playlist_id(user_id)

    if service2.is_user_change_playlist(user_id) or playlist_id is None:
        songs, total_page_count = service.get_songs(user_id, current_page, config.PAGE_SIZE)
    else:
        songs, total_page_count = service2.get_playlist_songs(user_id, current_page, config.PAGE_SIZE)

    page_text = "👇Список треков👇"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for song in songs:
        song_split = song.split(": ")
        song_id = song_split[0]
        song_name = song_split[1]

        # Присвоим имя кнопке для обработки ее нажатия
        button_callback_data = TRACK + "_" + song_id
        button = types.InlineKeyboardButton(song_name, callback_data=button_callback_data)

        keyboard.add(button)

    # Добавим навигацию
    create_navigation(current_page, total_page_count, keyboard, "next_page", "back_page")

    # Если сейчас редактируем плейлист, то добавим кнопку завершения
    if service2.is_user_change_playlist(user_id):
        end_change = types.InlineKeyboardButton("Завершить добавление", callback_data=END_CHANGE_PLAYLIST)
        keyboard.add(end_change)

    # Создадим страницу со списком треков
    message_id = service.get_bot_message_id(user_id)
    bot.edit_message_text(chat_id=user_id, text=page_text, message_id=message_id, reply_markup=keyboard,
                          parse_mode='html')


def create_playlists_page(user_id, current_page):
    # Количество записей на одной странице
    record_on_page = 8

    playlists, total_page_count = service2.get_playlists(user_id, current_page, record_on_page)

    page_text = "👇Список плейлистов👇"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for playlist in playlists:
        playlist_id = playlist[0]
        playlist_name = playlist[1]

        # Присвоим имя кнопке для обработки ее нажатия
        button_callback_data = PLAYLIST + "_" + str(playlist_id)
        button = types.InlineKeyboardButton(playlist_name, callback_data=button_callback_data)

        keyboard.add(button)

    # Добавим навигацию
    create_navigation(current_page, total_page_count, keyboard, "next_page", "back_page")

    # Создадим страницу со списком треков
    message_id = service.get_bot_message_id(user_id)
    bot.edit_message_text(chat_id=user_id, text=page_text, message_id=message_id, reply_markup=keyboard,
                          parse_mode='html')


def create_playlist_page(user_id, playlist_id):
    playlist_name = service2.get_playlist_name(playlist_id)
    page_text = f"{playlist_name}"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    tracks_list = types.InlineKeyboardButton("Список треков", callback_data=GET_TRACKS_LIST)
    add_track = types.InlineKeyboardButton("Добавить треки", callback_data=ADD_TRACK_TO_PLAYLIST)
    add_member = types.InlineKeyboardButton("Добавить участника", callback_data=ADD_MEMBER)
    delete_playlist = types.InlineKeyboardButton("Удалить", callback_data=DELETE_PLAYLIST)
    keyboard.add(tracks_list)
    keyboard.add(add_track)
    keyboard.add(add_member)
    keyboard.add(delete_playlist)

    # Создадим страницу со списком треков
    message_id = service.get_bot_message_id(user_id)
    bot.edit_message_text(chat_id=user_id, text=page_text, message_id=message_id, reply_markup=keyboard,
                          parse_mode='html')


def process_add_track_playlist(user_id, is_track):
    if is_track:
        text = "Введите ссылку"
        service.set_start_song_draft(user_id, True)
    else:
        text = "Введите название плейлиста"
        service2.set_start_playlist_draft(user_id, True)

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


def process_tracks_playlists(user_id, resend, is_tracks):
    page_text = "Выберите кнопку"
    message_id = service.get_bot_message_id(user_id)

    if is_tracks:
        add_callback = ADD_TRACK
        get_callback = GET_TRACKS_LIST
        add_button_text = "Добавить трек"
        get_list__button_text = "Список треков"
    else:
        add_callback = ADD_PLAYLIST
        get_callback = GET_PLAYLISTS_LIST
        add_button_text = "Добавить плейлист"
        get_list__button_text = "Список плейлистов"

    # Создаем Inline клавиатуру для главного меню
    keyboard = types.InlineKeyboardMarkup()
    add_button = types.InlineKeyboardButton(add_button_text, callback_data=add_callback)
    get_list_button = types.InlineKeyboardButton(get_list__button_text, callback_data=get_callback)
    keyboard.add(add_button)
    keyboard.add(get_list_button)

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
    engine = sqlalchemy.create_engine(config.DB_CONN_STRING, echo=True)
    Base.metadata.create_all(engine)
    service = services.UserService(engine)

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
            if not call.message:
                return

            user_id = call.from_user.id

            if call.data == TRACKS:
                service2.set_playlist_id(user_id, None)
                process_tracks_playlists(user_id, False, True)

            elif call.data == PLAYLISTS:
                process_tracks_playlists(user_id, False, False)

            elif call.data == ADD_TRACK:
                process_add_track_playlist(user_id, True)

            elif call.data == GET_TRACKS_LIST:
                service.set_current_page(user_id, 0, TRACKS)
                create_songs_page(user_id, 0)

            # TODO - Обработка нажатия кнопки "Вернуться"
            elif call.data == GO_BACK:
                xx = 0

            elif call.data == BACK_PAGE or call.data == NEXT_PAGE:
                previous_page, page_type = service.get_current_page(user_id)

                # Выберем направление перемещения(+1 -> следующая, -1 -> предыдущая)
                next_back_index = 1 if call.data == NEXT_PAGE else -1

                current_page = previous_page + next_back_index

                # Вычислим корректный номер текущей страницы
                # TODO - переписать get_total_page_tracks на get_total_page_count с учетом page_type
                if page_type == TRACKS:
                    total_page_count = service.get_total_page_tracks(user_id)
                    if current_page < 0:
                        current_page = total_page_count - 1
                    elif current_page > total_page_count - 1:
                        current_page = 0
                else:
                    total_page_count = service2.get_total_page_count(user_id, page_type)
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

            elif call.data.split("_")[0] == TRACK:
                track_id = call.data.split("_")[1]
                if service2.is_user_change_playlist(user_id):
                    add_track_to_playlist(user_id, track_id)
                else:
                    send_song_info_message(user_id, track_id)

            elif call.data.split("_")[0] == PLAYLIST:
                playlist_id = call.data.split("_")[1]
                service2.set_playlist_id(user_id, playlist_id)

                create_playlist_page(user_id, playlist_id)

            elif call.data == ADD_PLAYLIST:
                process_add_track_playlist(user_id, False)

            elif call.data == GET_PLAYLISTS_LIST:
                service.set_current_page(user_id, 0, PLAYLISTS)
                create_playlists_page(user_id, 0)

            elif call.data == ADD_TRACK_TO_PLAYLIST:
                service2.set_user_change_playlist(user_id, True)

                service.set_current_page(user_id, 0, TRACKS)
                create_songs_page(user_id, 0)

            elif call.data == END_CHANGE_PLAYLIST:
                service2.set_user_change_playlist(user_id, False)
                playlist_id = service2.get_playlist_id(user_id)
                create_playlist_page(user_id, playlist_id)

            # TODO
            elif call.data == CHANGE_TRACK:
                xx = 0
            
            elif match(rf"^{DELETE_TRACK}_*$", call.data) is None:
                # Находим song_id
                find_song_id = search(r"DELETE_TRACK_(.*)", call.data)
                assert find_song_id is not None
                song_id = find_song_id.group(1)

                print(song_id)
                name, _, _ = service.get_song(song_id)
                # Удаляем трек
                service.delete_song(song_id)

                # Пишем сообщение пользователю
                text = f"✅ Трек {name} успешно удалён"
                bot.send_message(chat_id=user_id, text=text, parse_mode='html')

                # Перерисовываем страницу со списком треков
                create_songs_page(user_id, 0)
            elif call.data == ADD_MEMBER:
                xx = 0
            elif call.data == DELETE_PLAYLIST:
                xx = 0

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
                if service.is_user_starting_song_draft(user_id):
                    sd: Type[SongDraft] = service.get_user_song_draft(user_id)
                    if sd.link is None:
                        service.set_draft_song_link(user_id, message.text)
                        text = "Введите автора"
                        bot.send_message(user_id, text, parse_mode='html')
                    elif sd.performer is None:
                        service.set_draft_song_performer(user_id, message.text)
                        text = "Введите имя трека"
                        bot.send_message(user_id, text, parse_mode='html')
                    elif sd.name is None:
                        service.set_draft_song_name(user_id, message.text)
                        service.create_song(user_id)
                        process_tracks_playlists(user_id, True, True)

                elif service2.is_user_starting_playlist_draft(user_id):
                    playlist_name = service2.get_user_playlist_draft(user_id)
                    if playlist_name is None:
                        service2.set_draft_playlist_name(user_id, message.text)
                        service2.create_playlist(user_id)

                        process_tracks_playlists(user_id, True, False)

            except Exception as e:
                print(repr(e))


    bot.polling()
