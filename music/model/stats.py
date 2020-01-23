from google.cloud.firestore import DocumentReference

import music.db.database as database

from spotframework.model.uri import Uri


class Stats:

    def __init__(self,
                 name: str,
                 username: str,
                 uri: str,

                 artists,
                 albums,
                 tracks,

                 user_total,

                 db_ref: DocumentReference):
        self.name = name
        self.username = username
        self.uri = Uri(uri)

        self._artists = artists
        self._albums = albums
        self._tracks = tracks

        self._user_total = user_total

        self.db_ref = db_ref

    def to_dict(self):
        return {
            'uri': str(self.uri),
            'name': self.name,
            'username': self.username,

            'artists': self.artists,
            'albums': self.albums,
            'tracks': self.tracks
        }

    def update_database(self, updates):
        database.update_stats(username=self.username, uri=self.uri, updates=updates)

    @property
    def artists(self):
        return self._artists

    @artists.setter
    def artists(self, value):
        database.update_stats(self.username, uri=self.uri, updates={'artists': value})
        self._artists = value

    @property
    def albums(self):
        return self._albums

    @albums.setter
    def albums(self, value):
        database.update_stats(self.username, uri=self.uri, updates={'albums': value})
        self._albums = value

    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, value):
        database.update_stats(self.username, uri=self.uri, updates={'tracks': value})
        self._tracks = value

    @property
    def user_total(self):
        return self._user_total

    @user_total.setter
    def user_total(self, value):
        database.update_stats(self.username, uri=self.uri, updates={'user_total': value})
        self._user_total = value
