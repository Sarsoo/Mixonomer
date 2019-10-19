from google.cloud import firestore
import music.db.database as database
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

    def reset(self):
        self.queried_playlists = []
        self.parts = []

    def get_recursive_parts(self, name):
        logger.info(f'getting part from {name} for {self.user_id}')

        self.reset()
        self.process_reference_by_name(name)

        return [i for i in {i for i in self.parts}]

    def process_reference_by_name(self, name):

        playlist_query = [i for i in
                          database.get_user_playlists_collection(self.user_id).where(u'name', u'==', name).stream()]

        if len(playlist_query) > 0:
            if len(playlist_query) == 1:

                if playlist_query[0].id not in self.queried_playlists:

                    playlist_doc = playlist_query[0].to_dict()
                    self.parts += playlist_doc['parts']

                    for i in playlist_doc['playlist_references']:
                        if i.id not in self.queried_playlists:
                            self.process_reference_by_reference(i)

                else:
                    logger.warning(f'playlist reference {name} already queried')

            else:
                logger.warning(f"multiple {name}'s found")

        else:
            logger.warning(f'playlist reference {name} not found')

    def process_reference_by_reference(self, ref):

        if ref.id not in self.queried_playlists:
            playlist_reference_object = ref.get().to_dict()
            self.parts += playlist_reference_object['parts']

            for i in playlist_reference_object['playlist_references']:
                self.process_reference_by_reference(i)

        else:
            logger.warning(f'playlist reference {ref.get().to_dict()["name"]} already queried')
