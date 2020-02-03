from datetime import datetime
import music.db.database as db


class Tag:

    def __init__(self,
                 tag_id: str,
                 name: str,
                 username: str,

                 db_ref,

                 tracks,
                 albums,
                 artists,

                 count: int,
                 proportion: float,
                 total_user_scrobbles: int,

                 last_updated: datetime):
        self.tag_id = tag_id
        self._name = name
        self.username = username

        self.db_ref = db_ref

        self._tracks = tracks
        self._albums = albums
        self._artists = artists

        self._count = count
        self._proportion = proportion
        self._total_user_scrobbles = total_user_scrobbles

        self._last_updated = last_updated

    def to_dict(self):
        return {
            'tag_id': self.tag_id,
            'name': self.name,
            'username': self.username,

            'tracks': self.tracks,
            'albums': self.albums,
            'artists': self.artists,

            'count': self.count,
            'proportion': self.proportion,

            'last_updated': self.last_updated
        }

    def update_database(self, updates):
        db.update_tag(username=self.username, tag_id=self.tag_id, updates=updates)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        db.update_tag(username=self.username, tag_id=self.tag_id, updates={'name': value})
        self._name = value

    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, value):
        db.update_tag(username=self.username, tag_id=self.tag_id, updates={'tracks': value})
        self._tracks = value

    @property
    def albums(self):
        return self._albums

    @albums.setter
    def albums(self, value):
        db.update_tag(username=self.username, tag_id=self.tag_id, updates={'albums': value})
        self._albums = value

    @property
    def artists(self):
        return self._artists

    @artists.setter
    def artists(self, value):
        db.update_tag(username=self.username, tag_id=self.tag_id, updates={'artists': value})
        self._artists = value

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        db.update_tag(username=self.username, tag_id=self.tag_id, updates={'count': value})
        self._count = value

    @property
    def proportion(self):
        return self._proportion

    @proportion.setter
    def proportion(self, value):
        db.update_tag(username=self.username, tag_id=self.tag_id, updates={'proportion': value})
        self._proportion = value

    @property
    def total_user_scrobbles(self):
        return self._total_user_scrobbles

    @total_user_scrobbles.setter
    def total_user_scrobbles(self, value):
        db.update_tag(username=self.username, tag_id=self.tag_id, updates={'total_user_scrobbles': value})
        self._total_user_scrobbles = value

    @property
    def last_updated(self):
        return self._last_updated

    @last_updated.setter
    def last_updated(self, value):
        db.update_tag(username=self.username, tag_id=self.tag_id, updates={'last_updated': value})
        self._last_updated = value
