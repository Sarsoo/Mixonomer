from typing import List
from enum import Enum
from datetime import datetime
from google.cloud.firestore import DocumentReference

import music.db.database as database


class Sort(Enum):
    shuffle = 1
    release_date = 2


class Playlist:
    def __init__(self,
                 uri: str,
                 name: str,
                 username: str,

                 db_ref: DocumentReference,

                 include_recommendations: bool,
                 recommendation_sample: int,
                 include_library_tracks: bool,

                 parts: List[str],
                 playlist_references: List[DocumentReference],
                 shuffle: bool,

                 sort: Sort = None,

                 description_overwrite: str = None,
                 description_suffix: str = None,

                 lastfm_stat_count: int = None,
                 lastfm_stat_album_count: int = None,
                 lastfm_stat_artist_count: int = None,

                 lastfm_stat_percent: int = None,
                 lastfm_stat_album_percent: int = None,
                 lastfm_stat_artist_percent: int = None,

                 lastfm_stat_last_refresh: datetime = None):
        self._uri = uri
        self.name = name
        self.username = username

        self.db_ref = db_ref

        self._include_recommendations = include_recommendations
        self._recommendation_sample = recommendation_sample
        self._include_library_tracks = include_library_tracks

        self._parts = parts
        self._playlist_references = playlist_references
        self._shuffle = shuffle

        self._sort = sort
        self._description_overwrite = description_overwrite
        self._description_suffix = description_suffix

        self._lastfm_stat_count = lastfm_stat_count
        self._lastfm_stat_album_count = lastfm_stat_album_count
        self._lastfm_stat_artist_count = lastfm_stat_artist_count

        self._lastfm_stat_percent = lastfm_stat_percent
        self._lastfm_stat_album_percent = lastfm_stat_album_percent
        self._lastfm_stat_artist_percent = lastfm_stat_artist_percent

        self._lastfm_stat_last_refresh = lastfm_stat_last_refresh

    def to_dict(self):
        return {
            'uri': self.uri,
            'name': self.name,

            'include_recommendations': self.include_recommendations,
            'recommendation_sample': self.recommendation_sample,
            'include_library_tracks': self.include_library_tracks,

            'parts': self.parts,
            'playlist_references': [i.get().to_dict().get('name') for i in self.playlist_references],
            'shuffle': self.shuffle,

            'sort': self.sort.name,
            'description_overwrite': self.description_overwrite,
            'description_suffix': self.description_suffix,

            'lastfm_stat_count': self.lastfm_stat_count,
            'lastfm_stat_album_count': self.lastfm_stat_album_count,
            'lastfm_stat_artist_count': self.lastfm_stat_artist_count,

            'lastfm_stat_percent': self.lastfm_stat_percent,
            'lastfm_stat_album_percent': self.lastfm_stat_album_percent,
            'lastfm_stat_artist_percent': self.lastfm_stat_artist_percent,

            'lastfm_stat_last_refresh': self.lastfm_stat_last_refresh
        }

    def update_database(self, updates):
        database.update_playlist(username=self.username, name=self.name, updates=updates)

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, value):
        database.update_playlist(self.username, self.name, {'uri': value})
        self._uri = value

    @property
    def include_recommendations(self):
        return self._include_recommendations

    @include_recommendations.setter
    def include_recommendations(self, value):
        database.update_playlist(self.username, self.name, {'include_recommendations': value})
        self._include_recommendations = value

    @property
    def recommendation_sample(self):
        return self._recommendation_sample

    @recommendation_sample.setter
    def recommendation_sample(self, value):
        database.update_playlist(self.username, self.name, {'recommendation_sample': value})
        self._recommendation_sample = value

    @property
    def include_library_tracks(self):
        return self._include_library_tracks

    @include_library_tracks.setter
    def include_library_tracks(self, value):
        database.update_playlist(self.username, self.name, {'include_library_tracks': value})
        self._include_library_tracks = value

    @property
    def parts(self):
        return self._parts

    @parts.setter
    def parts(self, value):
        database.update_playlist(self.username, self.name, {'parts': value})
        self._parts = value

    @property
    def playlist_references(self):
        return self._playlist_references

    @playlist_references.setter
    def playlist_references(self, value):
        database.update_playlist(self.username, self.name, {'playlist_references': value})
        self._playlist_references = value

    @property
    def shuffle(self):
        return self._shuffle

    @shuffle.setter
    def shuffle(self, value):
        database.update_playlist(self.username, self.name, {'shuffle': value})
        self._shuffle = value

    @property
    def sort(self):
        return self._sort

    @sort.setter
    def sort(self, value):
        database.update_playlist(self.username, self.name, {'sort': value.name})
        self._sort = value

    @property
    def description_overwrite(self):
        return self._description_overwrite

    @description_overwrite.setter
    def description_overwrite(self, value):
        database.update_playlist(self.username, self.name, {'description_overwrite': value})
        self._description_overwrite = value

    @property
    def description_suffix(self):
        return self._description_suffix

    @description_suffix.setter
    def description_suffix(self, value):
        database.update_playlist(self.username, self.name, {'description_suffix': value})
        self._description_suffix = value

    @property
    def lastfm_stat_count(self):
        return self._lastfm_stat_count

    @lastfm_stat_count.setter
    def lastfm_stat_count(self, value):
        database.update_playlist(self.username, self.name, {'lastfm_stat_count': value})
        self._lastfm_stat_count = value

    @property
    def lastfm_stat_album_count(self):
        return self._lastfm_stat_album_count

    @lastfm_stat_album_count.setter
    def lastfm_stat_album_count(self, value):
        database.update_playlist(self.username, self.name, {'lastfm_stat_album_count': value})
        self._lastfm_stat_album_count = value

    @property
    def lastfm_stat_artist_count(self):
        return self._lastfm_stat_artist_count

    @lastfm_stat_artist_count.setter
    def lastfm_stat_artist_count(self, value):
        database.update_playlist(self.username, self.name, {'lastfm_stat_artist_count': value})
        self._lastfm_stat_artist_count = value

    @property
    def lastfm_stat_percent(self):
        return self._lastfm_stat_percent

    @lastfm_stat_percent.setter
    def lastfm_stat_percent(self, value):
        database.update_playlist(self.username, self.name, {'lastfm_stat_percent': value})
        self._lastfm_stat_percent = value

    @property
    def lastfm_stat_album_percent(self):
        return self._lastfm_stat_album_percent

    @lastfm_stat_album_percent.setter
    def lastfm_stat_album_percent(self, value):
        database.update_playlist(self.username, self.name, {'lastfm_stat_album_percent': value})
        self._lastfm_stat_album_percent = value

    @property
    def lastfm_stat_artist_percent(self):
        return self._lastfm_stat_artist_percent

    @lastfm_stat_artist_percent.setter
    def lastfm_stat_artist_percent(self, value):
        database.update_playlist(self.username, self.name, {'lastfm_stat_artist_percent': value})
        self._lastfm_stat_artist_percent = value

    @property
    def lastfm_stat_last_refresh(self):
        return self._lastfm_stat_last_refresh

    @lastfm_stat_last_refresh.setter
    def lastfm_stat_last_refresh(self, value):
        database.update_playlist(self.username, self.name, {'lastfm_stat_last_refresh': value})
        self._lastfm_stat_last_refresh = value


class RecentsPlaylist(Playlist):
    def __init__(self,
                 uri: str,
                 name: str,
                 username: str,

                 db_ref: DocumentReference,

                 include_recommendations: bool,
                 recommendation_sample: int,
                 include_library_tracks: bool,

                 parts: List[str],
                 playlist_references: List[DocumentReference],
                 shuffle: bool,

                 sort: Sort = None,

                 description_overwrite: str = None,
                 description_suffix: str = None,

                 lastfm_stat_count: int = None,
                 lastfm_stat_album_count: int = None,
                 lastfm_stat_artist_count: int = None,

                 lastfm_stat_percent: int = None,
                 lastfm_stat_album_percent: int = None,
                 lastfm_stat_artist_percent: int = None,

                 lastfm_stat_last_refresh: datetime = None,

                 add_last_month: bool = False,
                 add_this_month: bool = False,
                 day_boundary: int = 7):
        super().__init__(uri=uri,
                         name=name,
                         username=username,

                         db_ref=db_ref,

                         include_recommendations=include_recommendations,
                         recommendation_sample=recommendation_sample,
                         include_library_tracks=include_library_tracks,

                         parts=parts,
                         playlist_references=playlist_references,
                         shuffle=shuffle,

                         sort=sort,

                         description_overwrite=description_overwrite,
                         description_suffix=description_suffix,

                         lastfm_stat_count=lastfm_stat_count,
                         lastfm_stat_album_count=lastfm_stat_album_count,
                         lastfm_stat_artist_count=lastfm_stat_artist_count,

                         lastfm_stat_percent=lastfm_stat_percent,
                         lastfm_stat_album_percent=lastfm_stat_album_percent,
                         lastfm_stat_artist_percent=lastfm_stat_artist_percent,

                         lastfm_stat_last_refresh=lastfm_stat_last_refresh)
        self._add_last_month = add_last_month
        self._add_this_month = add_this_month
        self._day_boundary = day_boundary

    def to_dict(self):
        response = super().to_dict()
        response.update({
            'add_last_month': self.add_last_month,
            'add_this_month': self.add_this_month,
            'day_boundary': self.day_boundary
        })
        return response

    @property
    def add_last_month(self):
        return self._add_last_month

    @add_last_month.setter
    def add_last_month(self, value):
        database.update_playlist(self.username, self.name, {'add_last_month': value})
        self._add_last_month = value

    @property
    def add_this_month(self):
        return self._add_this_month

    @add_this_month.setter
    def add_this_month(self, value):
        database.update_playlist(self.username, self.name, {'add_this_month': value})
        self._add_this_month = value

    @property
    def day_boundary(self):
        return self._day_boundary

    @day_boundary.setter
    def day_boundary(self, value):
        database.update_playlist(self.username, self.name, {'day_boundary': value})
        self._day_boundary = value
