# Что это за файл?
# Здесь методы которые необходимы для работы команд бота
# Что надо хранить?
# UserMessage: UserId - MessageId : для понимания какое сообщение редактировать у пользователя
# DraftSong: UserId - IsStarted - Link - Performer - Name :
#   - хранит информацию о том начал ли пользователь создавать песню и поля для песни
#   - None поле еще не было введено
# Songs: UserId - SongId - Link - Performer - Name : информация о песни
#
#
# Тут примерный api, будут изменения именно в ответе - пересядем на них быстро
# в этом файле хочется реализацию сохранения в бд / чтения из бд

user_message_dict = {}
user_songs = {}
song_id = 1

user_start_draft = False
user_draft_song_link = None
user_draft_song_name = None
user_draft_song_performer = None

user_page = 0
user_page_type = None


# Должны хранить
def get_bot_message_id(user_id):
    if user_id not in user_message_dict:
        return None

    return user_message_dict[user_id]


def set_bot_message_id(user_id, message_id):
    user_message_dict[user_id] = message_id


def is_user_starting_draft(user_id):
    global user_start_draft
    return user_start_draft


def set_start_song_draft(user_id, started):
    global user_start_draft
    user_start_draft = started


def get_user_song_draft(user_id):
    return user_draft_song_link, user_draft_song_performer, user_draft_song_name


def set_draft_song_link(user_id, song_link):
    global user_draft_song_link
    user_draft_song_link = song_link


def set_draft_song_name(user_id, song_name):
    global user_draft_song_name
    user_draft_song_name = song_name


def set_draft_song_performer(user_id, song_performer):
    global user_draft_song_performer
    user_draft_song_performer = song_performer


def create_song(user_id):
    link, performer, name = get_user_song_draft(user_id)
    if user_id not in user_songs:
        user_songs[user_id] = []
    user_songs[user_id].append((link, performer, name))

    # После добавления трека таблица драфта для юзера очищается
    global user_start_draft, user_draft_song_link, user_draft_song_name, user_draft_song_performer
    user_start_draft = False
    user_draft_song_link = None
    user_draft_song_name = None
    user_draft_song_performer = None


def get_total_page_tracks(user_id):
    total_page = 4
    return total_page


def get_songs(user_id, page, page_size):
    songs_arr = []

    for i in range(page_size - page):
        songs_arr.append((i, "song_name_" + str(i)))

    total_page = get_total_page_tracks(user_id)
    return songs_arr, total_page


def get_current_page(user_id):
    return user_page, user_page_type


def set_current_page(user_id, page, page_type):
    global user_page, user_page_type
    user_page = page
    user_page_type = page_type
