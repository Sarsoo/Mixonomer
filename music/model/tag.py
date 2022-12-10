from fireo.models import Model
from fireo.fields import TextField, DateTime, NumberField, ListField, BooleanField, IDField


class Tag(Model):
    class Meta:
        collection_name = 'tags'

    id = IDField()

    tag_id = TextField(required=True)
    name = TextField(required=True)
    username = TextField(required=True)

    tracks = ListField(default=[])
    albums = ListField(default=[])
    artists = ListField(default=[])

    count = NumberField(default=0)
    proportion = NumberField(default=0)
    total_user_scrobbles = NumberField(default=0)

    last_updated = DateTime()

    time_objects = BooleanField(default=False)
    total_time = TextField(default='00:00:00')
    total_time_ms = NumberField(default=0)

    def to_dict(self):
        to_return = super().to_dict()

        # remove unnecessary and sensitive fields
        to_return.pop('id', None)
        to_return.pop('key', None)

        return to_return
