from google.cloud import firestore

import logging

from spotframework.net.user import NetworkUser
from spotframework.net.network import Network

db = firestore.Client()

logger = logging.getLogger(__name__)


def create_playlist(username, name):

    logger.info(f'creating {username} / {name}')

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', username).stream()]

    if len(users) == 1:

        user_dict = users[0].to_dict()
        spotify_keys = db.document('key/spotify').get().to_dict()

        net = Network(NetworkUser(spotify_keys['clientid'],
                                  spotify_keys['clientsecret'],
                                  user_dict['refresh_token'],
                                  user_dict['access_token']))

        playlist = net.create_playlist(net.user.username, name)

        if playlist is not None:
            return playlist
        else:
            logger.error(f'no response received {username} / {name}')
            return None

    else:
        logger.error(f'{len(users)} users found')
        return None
