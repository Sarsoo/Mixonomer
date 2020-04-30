from fireo.models import Model
from fireo.fields import TextField, DateTime, NumberField, ListField


class Tag(Model):
    class Meta:
        collection_name = 'tags'

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

    def to_dict(self):
        to_return = super().to_dict()

        # remove unnecessary and sensitive fields
        to_return.pop('id', None)
        to_return.pop('key', None)

        return to_return
