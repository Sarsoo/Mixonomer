from google.cloud import firestore
import logging
from datetime import timedelta, datetime, timezone

from spotframework.net.network import Network as SpotifyNetwork
from fmframework.net.network import Network as FmNetwork
from music.db.user import DatabaseUser
from music.model.user import User

db = firestore.Client()

logger = logging.getLogger(__name__)


def refresh_token_database_callback(user):
    if isinstance(user, DatabaseUser):
        user_obj = User.collection.filter('username', '==', user.user_id.strip().lower()).get()
        if user_obj is None:
            logger.error(f'user {user} not found')

        user_obj.access_token = user.access_token
        user_obj.refresh_token = user.refresh_token
        user_obj.last_refreshed = user.last_refreshed
        user_obj.token_expiry = user.token_expiry

        user_obj.update()

        logger.debug(f'{user.user_id} database entry updated')
    else:
        logger.error('user has no attached id')


def get_authed_spotify_network(user):
    if user is not None:
        if user.spotify_linked:
            spotify_keys = db.document('key/spotify').get().to_dict()

            user_obj = DatabaseUser(client_id=spotify_keys['clientid'],
                                    client_secret=spotify_keys['clientsecret'],
                                    refresh_token=user.refresh_token,
                                    user_id=user.username,
                                    access_token=user.access_token)
            user_obj.on_refresh.append(refresh_token_database_callback)

            if user.last_refreshed is not None and user.token_expiry is not None:
                if user.last_refreshed + timedelta(seconds=user.token_expiry - 1) \
                        < datetime.now(timezone.utc):
                    user_obj.refresh_access_token()
            else:
                user_obj.refresh_access_token()

            user_obj.refresh_info()
            return SpotifyNetwork(user_obj)
        else:
            logger.error('user spotify not linked')
    else:
        logger.error(f'no user provided')


def get_authed_lastfm_network(user):
    if user is not None:
        if user.lastfm_username:
            fm_keys = db.document('key/fm').get().to_dict()
            return FmNetwork(username=user.lastfm_username, api_key=fm_keys['clientid'])
        else:
            logger.error(f'{user.username} has no last.fm username')
    else:
        logger.error(f'no user provided')
