from google.cloud import firestore
import logging
from datetime import timedelta, datetime, timezone
from typing import List, Optional
from werkzeug.security import check_password_hash

from spotframework.net.network import Network as SpotifyNetwork
from fmframework.net.network import Network as FmNetwork
from spotify.db.user import DatabaseUser

db = firestore.Client()

logger = logging.getLogger(__name__)


def refresh_token_database_callback(user):
    if isinstance(user, DatabaseUser):
        user_ref = get_user_doc_ref(user.user_id)

        user_ref.update({
            'access_token': user.access_token,
            'refresh_token': user.refresh_token,
            'last_refreshed': user.last_refreshed,
            'token_expiry': user.token_expiry
        })
        logger.debug(f'{user.user_id} database entry updated')
    else:
        logger.error('user has no attached id')


def get_authed_spotify_network(username):

    user = get_user_doc_ref(username)
    if user:
        user_dict = user.get().to_dict()

        if user_dict.get('spotify_linked', None):
            spotify_keys = db.document('key/spotify').get().to_dict()

            user_obj = DatabaseUser(client_id=spotify_keys['clientid'],
                                    client_secret=spotify_keys['clientsecret'],
                                    refresh_token=user_dict['refresh_token'],
                                    user_id=username,
                                    access_token=user_dict['access_token'])
            user_obj.on_refresh.append(refresh_token_database_callback)

            if user_dict['last_refreshed'] + timedelta(seconds=user_dict['token_expiry'] - 1) \
                    < datetime.now(timezone.utc):
                user_obj.refresh_access_token()

            user_obj.refresh_info()
            return SpotifyNetwork(user_obj)
        else:
            logger.error('user spotify not linked')
    else:
        logger.error(f'user {username} not found')


def get_authed_lastfm_network(username):

    user = get_user_doc_ref(username)
    if user:
        user_dict = user.get().to_dict()

        if user_dict.get('lastfm_username', None):
            fm_keys = db.document('key/fm').get().to_dict()

            return FmNetwork(username=user_dict['lastfm_username'], api_key=fm_keys['clientid'])
        else:
            logger.error(f'{username} has no last.fm username')
    else:
        logger.error(f'user {username} not found')


def check_user_password(username, password):

    user = get_user_doc_ref(user=username)
    if user:
        user_dict = user.get().to_dict()

        if check_password_hash(user_dict['password'], password):
            return True
        else:
            logger.error(f'password mismatch {username}')
    else:
        logger.error(f'user {username} not found')

    return False


def get_user_query_stream(user: str) -> List[firestore.DocumentSnapshot]:

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', user).stream()]

    if len(users) > 0:
        return users
    else:
        logger.warning(f'{user} not found')
        return []


def get_user_doc_ref(user: str) -> Optional[firestore.DocumentReference]:

    users = get_user_query_stream(user)

    if len(users) > 0:
        if len(users) == 1:
            return users[0].reference

        else:
            logger.error(f"multiple {user}'s found")
            return None

    else:
        logger.error(f'{user} not found')
        return None


def get_user_playlists_collection(user_id: str) -> firestore.CollectionReference:

    playlists = db.document(u'spotify_users/{}'.format(user_id)).collection(u'playlists')

    return playlists


def get_user_playlist_ref_by_username(user: str, playlist: str) -> Optional[firestore.CollectionReference]:

    user_ref = get_user_doc_ref(user)

    if user_ref:

        return get_user_playlist_ref_by_user_ref(user_ref, playlist)

    else:
        logger.error(f'{user} not found, looking up {playlist}')
        return None


def get_user_playlist_ref_by_user_ref(user_ref: firestore.DocumentReference,
                                      playlist: str) -> Optional[firestore.CollectionReference]:

    playlist_collection = get_user_playlists_collection(user_ref.id)

    username = user_ref.get().to_dict()['username']

    if playlist_collection:
        query = [i for i in playlist_collection.where(u'name', u'==', playlist).stream()]

        if len(query) > 0:
            if len(query) == 1:
                if query[0].exists:
                    return query[0].reference

                else:
                    logger.error(f'{playlist} for {username} does not exist')
                    return query[0]

            else:
                logger.error(f'{username} multiple response playlists found for {playlist}')
                return query[0]

        else:
            logger.error(f'{username} no playlist found for {playlist}')
            return None

    else:
        logger.error(f'{username} playlist collection not found, looking up {playlist}')
        return None
