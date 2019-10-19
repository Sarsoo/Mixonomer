from google.cloud import firestore

import logging
from datetime import datetime

import music.db.database as database

from spotfm.maths.counter import Counter
from spotframework.model.uri import Uri

db = firestore.Client()

logger = logging.getLogger(__name__)


def refresh_lastfm_stats(username, playlist_name):

    logger.info(f'refreshing {playlist_name} stats for {username}')

    fmnet = database.get_authed_lastfm_network(username=username)
    spotnet = database.get_authed_spotify_network(username=username)
    counter = Counter(fmnet=fmnet, spotnet=spotnet)

    database_ref = database.get_user_playlist_ref_by_username(user=username, playlist=playlist_name)

    playlist_dict = database_ref.get().to_dict()
    count = counter.count(Uri(playlist_dict['uri']))

    user_count = fmnet.get_user_scrobble_count()
    percent = round((count * 100) / user_count, 2)

    database_ref.update({
        'lastfm_stat_count': count,
        'lastfm_stat_percent': percent,
        'lastfm_stat_last_refresh': datetime.utcnow()
    })
