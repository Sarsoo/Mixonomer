from google.cloud import firestore

import logging

import music.db.database as database

db = firestore.Client()

logger = logging.getLogger(__name__)


def create_playlist(username, name):
    logger.info(f'creating spotify playlist for {username} / {name}')

    user = database.get_user(username)
    if user is not None:
        net = database.get_authed_spotify_network(username)

        playlist = net.create_playlist(net.user.username, name)

        if playlist is not None:
            return playlist
        else:
            logger.error(f'no response received {username} / {name}')
            return

    else:
        logger.error(f'{username} not found')
        return
