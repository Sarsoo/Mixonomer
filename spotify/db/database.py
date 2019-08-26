from google.cloud import firestore
import logging

db = firestore.Client()

logger = logging.getLogger(__name__)


def get_user_query_stream(user):

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', user).stream()]

    if len(users) > 0:
        return users
    else:
        logger.warning(f'{user} not found')
        return []


def get_user_doc_ref(user):

    users = get_user_query_stream(user)

    if len(users) > 0:
        if len(users) == 1:
            return db.collection(u'spotify_users').document(u'{}'.format(users[0].id))

        else:
            logger.error(f"multiple {user}'s found")
            return None

    else:
        logger.error(f'{user} not found')
        return None


def get_user_playlists_collection(user_id):

    playlists = db.document(u'spotify_users/{}'.format(user_id)).collection(u'playlists')

    return playlists


def get_user_playlist_ref(user, playlist):

    user_ref = get_user_doc_ref(user)

    if user_ref:

        playlist_collection = get_user_playlists_collection(user_ref.id)

        if playlist_collection:
            query = [i for i in playlist_collection.where(u'name', u'==', playlist).stream()]

            if len(query) > 0:
                if len(query) > 1:
                    return playlist_collection.document(u'{}'.format(query[0].id))

                else:
                    logger.error(f'{user} multiple response playlists found for {playlist}')
                    return query

            else:
                logger.error(f'{user} no playlist found for {playlist}')
                return None

        else:
            logger.error(f'{user} playlist collection not found, looking up {playlist}')
            return None

    else:
        logger.error(f'{user} not found, looking up {playlist}')
        return None
