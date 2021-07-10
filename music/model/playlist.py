from enum import Enum

from fireo.models import Model
from fireo.fields import TextField, BooleanField, DateTime, NumberField, ListField


class Sort(Enum):
    default = 1
    shuffle = 2
    release_date = 3


class Playlist(Model):
    """Smart playlist

    Args:
        Model ([type]): [description]

    Returns:
        [type]: [description]
    """
    class Meta:
        collection_name = 'playlists'

    uri = TextField()
    name = TextField(required=True)
    type = TextField(required=True)

    include_recommendations = BooleanField(default=False)
    recommendation_sample = NumberField(default=10)
    include_library_tracks = BooleanField(default=False)

    parts = ListField(default=[])
    playlist_references = ListField(default=[])
    shuffle = BooleanField(default=False)

    sort = TextField(default='release_date')
    description_overwrite = TextField()
    description_suffix = TextField()

    last_updated = DateTime()

    lastfm_stat_count = NumberField(default=0)
    lastfm_stat_album_count = NumberField(default=0)
    lastfm_stat_artist_count = NumberField(default=0)

    lastfm_stat_percent = NumberField(default=0)
    lastfm_stat_album_percent = NumberField(default=0)
    lastfm_stat_artist_percent = NumberField(default=0)

    lastfm_stat_last_refresh = DateTime()

    add_last_month = BooleanField(default=False)
    add_this_month = BooleanField(default=False)
    day_boundary = NumberField(default=21)

    include_spotify_owned = BooleanField(default=True)

    chart_range = TextField(default='MONTH')
    chart_limit = NumberField(default=50)

    mutable_keys = [
        'type',

        'include_recommendations',
        'recommendation_sample',
        'include_library_tracks',

        'parts',
        'playlist_references',
        'shuffle',

        'sort',
        'description_overwrite',
        'description_suffix',

        'add_last_month',
        'add_this_month',
        'day_boundary',
        
        'include_spotify_owned',

        'chart_range',
        'chart_limit'
    ]

    def to_dict(self):
        to_return = super().to_dict()

        to_return["playlist_references"] = [i.get().to_dict().get('name') for i in to_return['playlist_references']]

        # remove unnecessary and sensitive fields
        to_return.pop('id', None)
        to_return.pop('key', None)

        return to_return
