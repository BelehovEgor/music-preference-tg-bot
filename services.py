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
import math
import uuid
from typing import Type

import sqlalchemy
from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session

from models import *
from models import SongDraft

user_message_dict = {}
user_songs = {}
song_id = 1

user_start_draft = False
user_draft_song_link = None
user_draft_song_name = None
user_draft_song_performer = None

user_page = 0
user_page_type = None


class UserService:
    def __init__(self, db_engine: sqlalchemy.Engine):
        self.engine = db_engine

    def get_bot_message_id(self, user_id):
        with Session(self.engine) as session:
            uem = session.get(UserEditingMessage, {"user_id": user_id})
            if uem is not None:
                return uem.message_id
            else:
                return None

    def set_bot_message_id(self, user_id, message_id):
        with Session(self.engine) as session:
            uem = UserEditingMessage(user_id=user_id, message_id=message_id)
            session.merge(uem)  # upsert
            session.commit()

    def is_user_starting_song_draft(self, user_id):
        with Session(self.engine) as session:
            sd = session.get(SongDraft, {"user_id": user_id})
            if sd is not None:
                return sd.is_started
            else:
                return False

    def is_user_starting_playlist_draft(self, user_id):
        with Session(self.engine) as session:
            sd = session.get(PlaylistDraft, {"user_id": user_id})
            if sd is not None:
                return sd.is_started
            else:
                return False

    def set_start_song_draft(self, user_id, started):
        with Session(self.engine) as session:
            draft = SongDraft(user_id=user_id, is_started=started, link=None, performer=None, name=None)
            session.merge(draft)
            session.commit()

    def get_user_song_draft(self, user_id) -> Type[SongDraft]:
        with Session(self.engine) as session:
            return session.get_one(SongDraft, {"user_id": user_id})

    def set_start_playlist_draft(self, user_id, started):
        with Session(self.engine) as session:
            draft = PlaylistDraft(user_id=user_id, is_started=started, name=None)
            session.merge(draft)
            session.commit()

    def get_user_playlist_draft(self, user_id) -> Type[PlaylistDraft]:
        with Session(self.engine) as session:
            return session.get_one(PlaylistDraft, {"user_id": user_id})

    def set_draft_song_link(self, user_id, song_link):
        with Session(self.engine) as session:
            sd = session.get_one(SongDraft, {"user_id": user_id})
            sd.link = song_link
            session.commit()

    def set_draft_song_name(self, user_id, song_name):
        with Session(self.engine) as session:
            sd = session.get_one(SongDraft, {"user_id": user_id})
            sd.name = song_name
            session.commit()

    def set_draft_song_performer(self, user_id, song_performer):
        with Session(self.engine) as session:
            sd = session.get_one(SongDraft, {"user_id": user_id})
            sd.performer = song_performer
            session.commit()

    def set_draft_playlist_name(self, user_id, playlist_name):
        with Session(self.engine) as session:
            sd = session.get_one(PlaylistDraft, {"user_id": user_id})
            sd.name = playlist_name
            session.commit()

    def create_song(self, user_id):
        sd: Type[SongDraft] = self.get_user_song_draft(user_id)
        song = Song(user_id=user_id, song_id=uuid.uuid4(), name=sd.name, link=sd.link, performer=sd.performer)
        with Session(self.engine) as session:
            session.add(song)
            session.commit()
        # После добавления трека таблица драфта для юзера очищается
        self.set_start_song_draft(user_id, started=False)

    def create_playlist(self, user_id):
        sd: Type[PlaylistDraft] = self.get_user_playlist_draft(user_id)
        playlist = Playlist(user_id=user_id, playlist_id=uuid.uuid4(), name=sd.name)
        with Session(self.engine) as session:
            session.add(playlist)
            session.commit()
        self.set_start_playlist_draft(user_id, started=False)

    def get_total_page_tracks(self, user_id):
        with Session(self.engine) as session:
            songs_count = session.scalars(select(func.count(Song.song_id)).where(Song.user_id == user_id)).one()
            return math.ceil(songs_count / config.PAGE_SIZE)

    def get_total_page_playlists(self, user_id):
        with Session(self.engine) as sesssion:
            playlists_count = sesssion.scalars(select(func.count(Playlist.playlist_id)).where(Playlist.user_id == user_id)).one()
            return math.ceil(playlists_count / config.PAGE_SIZE)

    def get_songs(self, user_id, page, page_size):
        songs_arr = []
        with Session(self.engine) as session:
            songs = session.scalars(select(Song).where(Song.user_id == user_id).limit(page_size).offset(page * page_size)).all()

        for song in songs:
            songs_arr.append(str(song))

        total_page = self.get_total_page_tracks(user_id)
        return songs_arr, total_page

    def get_playlists(self, user_id, page, page_size):
        playlists_arr = []
        with Session(self.engine) as session:
            playlists = session.scalars(select(Playlist).where(Playlist.user_id == user_id).limit(page_size).offset(page * page_size)).all()

        for playlist in playlists:
            playlists_arr.append(str(playlist))

        total_page = self.get_total_page_playlists(user_id)
        return playlists_arr, total_page

    def get_song(self, song_id):
        with Session(self.engine) as session:
            song = session.get_one(Song, {"song_id": uuid.UUID(song_id)})
            return song.name, song.performer, song.link

    def get_playlist(self, playlist_id):
        with Session(self.engine) as session:
            playlist = session.get_one(Playlist, {"playlist_id": uuid.UUID(playlist_id)})
            return playlist.name

    def set_user_change_playlist(self, playlist_id, is_user_change):
        with Session(self.engine) as session:
            session.query(Playlist).filter(Playlist.playlist_id == uuid.UUID(playlist_id)).update({Playlist.is_user_change: is_user_change}, synchronize_session=False)
            session.commit()

    def get_is_user_change_playlist(self, playlist_id):
        if playlist_id is None:
            return False

        with Session(self.engine) as session:
            playlist = session.get_one(Playlist, {"playlist_id": uuid.UUID(playlist_id)})
            return playlist.is_user_change

    def set_current_playlist(self, user_id, playlist_id):
        with Session(self.engine) as session:
            if playlist_id is None:
                session.query(Playlist).filter(Playlist.user_id == user_id).update({Playlist.is_current: False}, synchronize_session=False)
            else:
                session.query(Playlist).filter(Playlist.playlist_id == uuid.UUID(playlist_id)).update({Playlist.is_current: True}, synchronize_session=False)
            session.commit()

    def get_current_playlist(self, user_id):
        with Session(self.engine) as session:
            playlists = session.scalars(select(Playlist).where(Playlist.user_id == user_id)).all()

            current_playlist = None
            for playlist in playlists:
                if playlist.is_current is True:
                    current_playlist = str(playlist.playlist_id)
                    break

        return current_playlist
    
    def set_song_to_playlist(self, song_id, playlist_id):
        playlist_song = PlaylistSong(playlist_id=uuid.UUID(playlist_id), song_id=uuid.UUID(song_id))
        with Session(self.engine) as session:
            session.add(playlist_song)
            session.commit()

    def get_total_page_playlists_songs(self, playlist_id):
        with Session(self.engine) as session:
            playlist_songs_count = session.scalars(select(func.count(PlaylistSong.playlist_id)).where(PlaylistSong.playlist_id == playlist_id)).one()
            return math.ceil(playlist_songs_count / config.PAGE_SIZE)

    def get_playlist_songs(self, playlist_id, page, page_size):
        playlist_songs_arr = []
        with Session(self.engine) as session:
            playlists_songs = session.query(PlaylistSong).filter(PlaylistSong.playlist_id == uuid.UUID(playlist_id)).all()

            playlist_song_ids = [playlist_song.song_id for playlist_song in playlists_songs]

            playlist_songs = session.query(Song).filter(Song.song_id.in_(playlist_song_ids)).all()

            playlist_songs_arr = [str(song) for song in playlist_songs]

        total_page = self.get_total_page_playlists(playlist_id)
        return playlist_songs_arr, total_page

    def delete_song(self, song_id):
        with Session(self.engine) as session:
            statement = delete(Song).where(Song.song_id == uuid.UUID(song_id))
            session.execute(statement)
            session.commit()

            # Удаляем из связующей таблицы, чтобы не говнякать
            statement = delete(PlaylistSong).where(PlaylistSong.song_id == uuid.UUID(song_id))
            session.execute(statement)
            session.commit()

    def delete_playlist(self, playlist_id):
        with Session(self.engine) as session:
            statement = delete(Playlist).where(Playlist.playlist_id == uuid.UUID(playlist_id))
            session.execute(statement)
            session.commit()

            # Удаляем из связующей таблицы, чтобы не говнякать
            statement = delete(PlaylistSong).where(PlaylistSong.playlist_id == uuid.UUID(playlist_id))
            session.execute(statement)
            session.commit()

    def get_current_page(self, user_id):
        with Session(self.engine) as session:
            ucp = session.get_one(UserCurrentPage, {"user_id": user_id})
            return ucp.page, ucp.page_type

    def set_current_page(self, user_id, page: int, page_type: str):
        with Session(self.engine) as session:
            ucp = UserCurrentPage(user_id=user_id, page=page, page_type=page_type)
            session.merge(ucp)
            session.commit()
