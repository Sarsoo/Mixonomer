import logging
from typing import Optional

import music.db.database as database
from spotframework.net.network import SpotifyNetworkException
from spotframework.model.playlist import FullPlaylist

from music.model.user import User

logger = logging.getLogger(__name__)


def create_playlist(user: User, name: str) -> Optional[FullPlaylist]:
    """Create a new playlist on the user's Spotify account

    For creating new playlists, create and return a new playlist object

    Args:
        user (User): Subject user
        name (str): Name of new playlist

    Returns:
        Optional[FullPlaylist]: New playlist object if created
    """

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
