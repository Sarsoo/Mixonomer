from fireo.models import Model
from fireo.fields import TextField, BooleanField, DateTime, NumberField, ListField


class Config(Model):
    """Service-level config data structure for app keys and settings
    """

    class Meta:
        collection_name = 'config'
        """Set correct path in Firestore
        """

    spotify_client_id = TextField()
    spotify_client_secret = TextField()
    last_fm_client_id = TextField()

    playlist_cloud_operating_mode = TextField()  # task, function
    """Determines whether playlist and tag update operations are done by Cloud Tasks or Functions
    """
    secret_key = TextField()
    jwt_secret_key = TextField()
