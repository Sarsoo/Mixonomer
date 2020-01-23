from google.cloud import firestore

import logging
from datetime import datetime

import music.db.database as database

from spotfm.maths.counter import Counter
from spotframework.model.uri import Uri

db = firestore.Client()

logger = logging.getLogger(__name__)


def refresh_stats(username, uri: Uri = None, uri_string: str = None):

    if uri is None and uri_string is None:
        raise ValueError('no uri to analyse')

    if uri is None:
        uri = Uri(uri_string)

    logger.info(f'refreshing {uri} stats for {username}')

    fmnet = database.get_authed_lastfm_network(username=username)
    spotnet = database.get_authed_spotify_network(username=username)
    counter = Counter(fmnet=fmnet, spotnet=spotnet)

    playlist = spotnet.get_playlist(uri=uri)

    track_count = counter.count_playlist(playlist=playlist)
    user_count = fmnet.get_user_scrobble_count()

    stat = database.get_stat(username=username, uri=uri)

    if stat is None:
        stat = database.create_stat(username=username, uri=uri)

    stat.update_database({})
