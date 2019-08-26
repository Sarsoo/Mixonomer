from google.cloud import firestore
import spotify.db.database as database
import logging

db = firestore.Client()
logger = logging.getLogger(__name__)


class PartGenerator:

    def __init__(self, user_id=None, username=None):
        self.queried_playlists = []
        self.parts = []

        if user_id:
            self.user_id = user_id
        elif username:
            user_doc = database.get_user_doc_ref(username)
            if user_doc:
                self.user_id = user_doc.id
            else:
                raise LookupError(f'{username} not found')
        else:
            raise NameError('no user info provided')

    def get_recursive_parts(self, name):
        logger.info(f'getting part from {name} for {self.user_id}')

        self.queried_playlists = []
        self.parts = []
        self._generate_parts(name)

        return [i for i in {i for i in self.parts}]

    def _generate_parts(self, name):
        self.queried_playlists.append(name)

        playlist_query = [i.to_dict() for i in
                          database.get_user_playlists_collection(self.user_id).where(u'name', '==', name).stream()]

        if len(playlist_query) > 0:
            if len(playlist_query) == 1:

                playlist_doc = playlist_query[0]
                self.parts += playlist_doc['parts']

                for i in playlist_doc['playlist_references']:
                    if i not in self.queried_playlists:
                        self._generate_parts(i)

            else:
                logger.warning(f"multiple {name}'s found")

        else:
            logger.warning(f'playlist {name} not found')
