import uuid
from typing import Optional

import sqlalchemy as db
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

import config


# Что это за файл?
# Здесь методы которые необходимы для работы команд бота
# Что надо хранить?
# UserMessage: UserId - MessageId : для понимания какое сообщение редактировать у пользователя
# DraftSong: UserId - IsStarted - Link - Performer - Name :
#   - хранит информацию о том начал ли пользователь создавать песню и поля для песни
#   - None поле еще не было введено
# Songs: UserId - SongId - Link - Performer - Name : информация о песни
# PlaylistDraft: UserId - IsStarted - Name :
#   - хранить информацию о том начал ли пользователь создавать плейлист и поле для плейлиста
# Playlist: UserId - PlaylistId - Name : информацию о плейлисте
#
# Тут примерный api, будут изменения именно в ответе - пересядем на них быстро
# в этом файле хочется реализацию сохранения в бд / чтения из бд


class Base(DeclarativeBase):
    pass


class UserEditingMessage(Base):
    __tablename__ = "user_editing_message"
    user_id: Mapped[str] = mapped_column(primary_key=True)
    message_id: Mapped[str]

    def __repr__(self) -> str:
        return (
            f"UserEditingMessage: user_id={self.user_id}, message_id={self.message_id}"
        )


class UserCurrentPage(Base):
    __tablename__ = "user_current_page"
    user_id: Mapped[str] = mapped_column(primary_key=True)
    page: Mapped[int]
    page_type: Mapped[str]

    def __repr__(self) -> str:
        return f"UserCurrentPage: user_id={self.user_id}, page={self.page}, page_type={self.page_type}"


class SongDraft(Base):
    __tablename__ = "songs_draft"
    user_id: Mapped[str] = mapped_column(primary_key=True)
    is_started: Mapped[bool] = mapped_column(default=False)
    link: Mapped[Optional[str]] = mapped_column(default=None)
    performer: Mapped[Optional[str]] = mapped_column(default=None)
    name: Mapped[Optional[str]] = mapped_column(default=None)


class Song(Base):
    __tablename__ = "songs"
    song_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[str]
    link: Mapped[str]
    performer: Mapped[str]
    name: Mapped[str]

    def __repr__(self):
        return f"{self.song_id}: {self.name}"

    playlists = relationship("PlaylistSong", back_populates="song")


class PlaylistDraft(Base):
    __tablename__ = "playlist_draft"
    user_id: Mapped[str] = mapped_column(primary_key=True)
    is_started: Mapped[bool] = mapped_column(default=False)
    name: Mapped[Optional[str]] = mapped_column(default=None)


class Playlist(Base):
    __tablename__ = "playlists"
    playlist_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[str]
    name: Mapped[str]
    is_user_change: Mapped[bool] = mapped_column(default=False)
    is_current: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f"{self.playlist_id}: {self.name}"

    songs = relationship("PlaylistSong", back_populates="playlist")


class PlaylistSong(Base):
    __tablename__ = "playlist_song"
    playlist_song_id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(UUID(as_uuid=True), ForeignKey("playlists.playlist_id"))
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.song_id"))

    playlist = relationship("Playlist", back_populates="songs")
    song = relationship("Song", back_populates="playlists")


if __name__ == "__main__":
    engine = db.create_engine(config.DB_CONN_STRING, echo="True")
    Base.metadata.create_all(engine)
    conn = engine.connect()
