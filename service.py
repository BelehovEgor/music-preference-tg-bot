user_message_dict = {}
user_songs = {}
song_id = 1

user_start_draft = False
user_draft_song_link = None
user_draft_song_name = None
user_draft_song_performer = None


# Должны хранить
def get_bot_message_id(user_id):
    return user_message_dict[user_id]


def set_bot_message_id(user_id, message_id):
    user_message_dict[user_id] = message_id


def get_user_song_draft(user_id):
    return user_draft_song_link, user_draft_song_performer, user_draft_song_name


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


def is_user_starting_draft(user_id):
    global user_start_draft
    return user_start_draft


def set_draft_song_link(user_id, song_link):
    global user_draft_song_link
    user_draft_song_link = True


def set_draft_song_name(user_id, song_name):
    global user_draft_song_name
    user_draft_song_name = True


def set_draft_song_performer(user_id, song_performer):
    global user_draft_song_performer
    user_draft_song_performer = True


def start_song_draft(user_id):
    global user_start_draft
    user_start_draft = True
