from fireo.models import Model
from fireo.fields import TextField, NumberField, IDField


class Config(Model):
    """Service-level config data structure for app keys and settings
    """

    class Meta:
        collection_name = 'config'
        """Set correct path in Firestore
        """

    id = IDField()

    spotify_callback = TextField()
    apns_team_id = TextField()
    apns_key_id = TextField()
    playlist_cloud_operating_mode = TextField()  # task, function
    """Determines whether playlist and tag update operations are done by Cloud Tasks or Functions
    """
    jwt_max_length = NumberField()
    jwt_default_length = NumberField()
