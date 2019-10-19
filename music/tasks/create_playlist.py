from google.cloud import firestore

import logging

import music.db.database as database

db = firestore.Client()

logger = logging.getLogger(__name__)


def create_playlist(username, name):

    logger.info(f'creating {username} / {name}')

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', username).stream()]

    if len(users) == 1:

        net = database.get_authed_spotify_network(username)

        playlist = net.create_playlist(net.user.username, name)

        if playlist is not None:
            return playlist
        else:
            logger.error(f'no response received {username} / {name}')
            return None

    else:
        logger.error(f'{len(users)} users found')
        return None
