from fireo.models import Model
from fireo.fields import TextField, BooleanField, DateTime, NumberField, ListField


class Config(Model):
    class Meta:
        collection_name = 'config'

    spotify_client_id = TextField()
    spotify_client_secret = TextField()
    last_fm_client_id = TextField()

    playlist_cloud_operating_mode = TextField()  # task, function
    secret_key = TextField()
