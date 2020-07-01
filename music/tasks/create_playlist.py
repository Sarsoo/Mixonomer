import logging

import music.db.database as database
from spotframework.net.network import SpotifyNetworkException

logger = logging.getLogger(__name__)


def create_playlist(user, name):

    if user is None:
        logger.error(f'username not provided')
        return

    logger.info(f'creating spotify playlist for {user.username} / {name}')
    net = database.get_authed_spotify_network(user)

    try:
        return net.create_playlist(net.user.user.display_name, name)
    except SpotifyNetworkException:
        logger.exception(f'error ocurred {user.username} / {name}')
        return
