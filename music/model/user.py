from fireo.models import Model
from fireo.fields import TextField, BooleanField, DateTime, NumberField

from werkzeug.security import check_password_hash


class User(Model):
    class Meta:
        collection_name = 'spotify_users'

    username = TextField(required=True)
    password = TextField(required=True)
    email = TextField()
    type = TextField(default="user")

    last_login = DateTime()
    last_refreshed = DateTime()
    locked = BooleanField(default=False, required=True)
    validated = BooleanField(default=True, required=True)

    spotify_linked = BooleanField(default=False, required=True)
    access_token = TextField()
    refresh_token = TextField()
    token_expiry = NumberField()

    lastfm_username = TextField()

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
