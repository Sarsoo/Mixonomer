import logging

from fireo.models import Model
from fireo.fields import TextField, BooleanField, DateTime, NumberField, ListField, IDField

from music.model.playlist import Playlist

from werkzeug.security import check_password_hash

logger = logging.getLogger(__name__)


class User(Model):
    class Meta:
        collection_name = 'spotify_users'

    id = IDField()

    username = TextField(required=True)
    password = TextField(required=True)
    email = TextField()
    type = TextField(default="user")

    last_login = DateTime()
    last_keygen = DateTime()
    last_refreshed = DateTime()
    locked = BooleanField(default=False, required=True)
    validated = BooleanField(default=True, required=True)

    spotify_linked = BooleanField(default=False, required=True)
    access_token = TextField()
    refresh_token = TextField()
    token_expiry = NumberField()

    lastfm_username = TextField()

    apns_tokens = ListField(default=[])
    notify = BooleanField(default=False)
    notify_playlist_updates = BooleanField(default=False)
    notify_tag_updates = BooleanField(default=False)
    notify_admins = BooleanField(default=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        to_return = super().to_dict()

        # remove unnecessary and sensitive fields
        to_return.pop('password', None)
        to_return.pop('access_token', None)
        to_return.pop('refresh_token', None)
        to_return.pop('token_expiry', None)
        to_return.pop('id', None)
        to_return.pop('key', None)

        return to_return

    def get_playlist(self, playlist_name: str, single_return=True, raise_error=True):
        """Get a user's playlist by name with smart case sensitivity

        Will return an exact match if possible, otherwise will return the first case-insensitive match

        Args:
            playlist_name (str): Subject playlist name
            single_return (bool, optional): Return the best match, otherwise return (<exact>, <all matches>). <exact> will be None if not found. Defaults to True.
            raise_error (bool, optional): Raise a NameError if nothing found. Defaults to True.

        Raises:
            NameError: If no matching playlists found

        Returns:
            Optional[Playlist] or (<exact>, <all matches>): Found user's playlists
        """

        smart_playlists = Playlist.collection.parent(self.key).fetch()

        exact_match = None
        matches = list()
        for playlist in smart_playlists:
            if playlist.name == playlist_name:
                exact_match = playlist
            if playlist.name.lower() == playlist_name.lower():
                matches.append(playlist)

        if len(matches) == 0:
            # NO PLAYLIST FOUND
            logger.critical(f'playlist not found {self.username} / {playlist_name}')
            if raise_error:
                raise NameError(f'Playlist {playlist_name} not found for {self.username}')
            else:
                return None

        if single_return:
            if exact_match:
                return exact_match
            else:
                return matches[0]
        else:
            return exact_match, matches

    def get_playlists(self):
        """Get all playlists for a user

        Returns:
            List[Playlist]: List of users playlists 
        """
        return Playlist.collection.parent(self.key).fetch()


def get_admins():
    return User.collection.filter('type', '==', 'admin').fetch()