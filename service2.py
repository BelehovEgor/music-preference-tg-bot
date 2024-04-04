from models import Song

user_playlists = {}
user_start_playlist_draft = False
user_draft_playlist_name = None

current_playlist_id = None
user_change_playlist = False

playlists = {}
songs_arr = []


def is_user_starting_playlist_draft(user_id):
    global user_start_playlist_draft
    return user_start_playlist_draft


def set_start_playlist_draft(user_id, started):
    global user_start_playlist_draft
    user_start_playlist_draft = started


def get_user_playlist_draft(user_id):
    global user_draft_playlist_name
    xx = user_draft_playlist_name

    return user_draft_playlist_name


def set_draft_playlist_name(user_id, playlist_name):
    global user_draft_playlist_name
    user_draft_playlist_name = playlist_name


def create_playlist(user_id):
    name = get_user_playlist_draft(user_id)
    if user_id not in user_playlists:
        user_playlists[user_id] = []
    user_playlists[user_id].append(name)

    # После добавления трека таблица драфта для юзера очищается
    global user_start_playlist_draft, user_draft_playlist_name
    user_start_playlist_draft = False
    user_draft_playlist_name = None


def get_total_page_count(user_id, page_type):
    total_page_tracks = 8
    total_page_playlists = 4
    if page_type == "playlists":
        return total_page_playlists
    return total_page_tracks


def get_playlists(user_id, page, page_size):
    playlists_arr = []

    for i in range(page_size - page):
        playlists_arr.append((i, "playlist_name_" + str(i)))

    total_page = get_total_page_count(user_id, "playlists")
    return playlists_arr, total_page


def get_playlist_songs(user_id, page, page_size):
    playlist_id = get_playlist_id(user_id)
    global songs_arr
    songs = []

    for i in songs_arr:
        songs.append("song_id: playlist_song_name_" + str(i))

    total_page = 4
    return songs, total_page


def is_user_change_playlist(user_id):
    return user_change_playlist


def set_user_change_playlist(user_id, started):
    global user_change_playlist
    user_change_playlist = started


def get_playlist_id(user_id):
    return current_playlist_id


def set_playlist_id(user_id, playlist_id):
    global current_playlist_id
    current_playlist_id = playlist_id


def get_playlist_name(playlist_id):
    playlist_name = "123"
    return playlist_name


# сохранение track_id в массив tracks для конкретного playlist по playlist_id
def save_song_to_playlist(track_id, playlist_id):
    global songs_arr
    songs_arr.append(track_id)
