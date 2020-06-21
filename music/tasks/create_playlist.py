from google.cloud import firestore

import logging

import music.db.database as database

db = firestore.Client()

logger = logging.getLogger(__name__)


def create_playlist(user, name):

    if user is None:
        logger.error(f'username not provided')
        return

    logger.info(f'creating spotify playlist for {user.username} / {name}')
    net = database.get_authed_spotify_network(user)

    playlist = net.create_playlist(net.user.username, name)

    if playlist is not None:
        return playlist
    else:
        logger.error(f'no response received {user.username} / {name}')
        return
