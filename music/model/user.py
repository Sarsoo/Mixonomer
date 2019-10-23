from datetime import datetime
from enum import Enum

from werkzeug.security import generate_password_hash, check_password_hash

import music.db.database as database


class User:
    class Type(Enum):
        user = 1
        admin = 2

    def __init__(self,
                 username: str,
                 password: str,
                 db_ref,
                 email: str,
                 user_type: Type,
                 last_login: datetime,
                 last_refreshed: datetime,
                 locked: bool,
                 validated: bool,

                 spotify_linked: bool,
                 access_token: str,
                 refresh_token: str,
                 token_expiry: int,

                 lastfm_username: str = None):
        self.username = username
        self._password = password
        self.db_ref = db_ref
        self._email = email
        self._type = user_type

        self._last_login = last_login
        self._last_refreshed = last_refreshed
        self._locked = locked
        self._validated = validated

        self._spotify_linked = spotify_linked
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._token_expiry = token_expiry

        self._lastfm_username = lastfm_username

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'type': self.user_type.name,
            'last_login': self.last_login,
            'spotify_linked': self.spotify_linked,
            'lastfm_username': self.lastfm_username
        }

    def update_database(self, updates):
        database.update_user(username=self.username, updates=updates)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        pw_hash = generate_password_hash(value)
        database.update_user(self.username, {'password': pw_hash})
        self._password = pw_hash

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        database.update_user(self.username, {'email': value})
        self._email = value

    @property
    def user_type(self):
        return self._type

    @user_type.setter
    def user_type(self, value):
        database.update_user(self.username, {'type': value})
        self._type = value

    @property
    def last_login(self):
        return self._last_login

    @last_login.setter
    def last_login(self, value):
        database.update_user(self.username, {'last_login': value})
        self._last_login = value

    @property
    def last_refreshed(self):
        return self._last_refreshed

    @last_refreshed.setter
    def last_refreshed(self, value):
        database.update_user(self.username, {'last_refreshed': value})
        self._last_refreshed = value

    @property
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, value):
        database.update_user(self.username, {'locked': value})
        self._locked = value

    @property
    def validated(self):
        return self._validated

    @validated.setter
    def validated(self, value):
        database.update_user(self.username, {'validated': value})
        self._validated = value

    @property
    def spotify_linked(self):
        return self._spotify_linked

    @spotify_linked.setter
    def spotify_linked(self, value):
        database.update_user(self.username, {'spotify_linked': value})
        self._spotify_linked = value

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        database.update_user(self.username, {'access_token': value})
        self._access_token = value

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value):
        database.update_user(self.username, {'refresh_token': value})
        self._refresh_token = value

    @property
    def token_expiry(self):
        return self._token_expiry

    @token_expiry.setter
    def token_expiry(self, value):
        database.update_user(self.username, {'refresh_token': value})
        self._token_expiry = value

    @property
    def lastfm_username(self):
        return self._lastfm_username

    @lastfm_username.setter
    def lastfm_username(self, value):
        database.update_user(self.username, {'lastfm_username': value})
        self._lastfm_username = value
