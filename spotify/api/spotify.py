from google.cloud import firestore

import logging

from spotframework.net.user import User
from spotframework.net.network import Network

db = firestore.Client()

logger = logging.getLogger(__name__)


def create_playlist(username, name):

    logger.info(f'creating {username} / {name}')

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', username).stream()]

    if len(users) == 1:

        user_dict = users[0].to_dict()
        spotify_keys = db.document('key/spotify').get().to_dict()

        net = Network(User(spotify_keys['clientid'],
                           spotify_keys['clientsecret'],
                           user_dict['access_token'],
                           user_dict['refresh_token']))

        resp = net.create_playlist(net.user.username, name)

        if resp and resp.get('id', None):
            return resp['id']
        else:
            logger.error(f'no response received {username} / {name}')
            return None

    else:
        logger.error(f'{len(users)} users found')
        return None
