from google.cloud import firestore

import logging
from datetime import datetime

import music.db.database as database

from spotfm.maths.counter import Counter
from spotframework.model.uri import Uri

db = firestore.Client()

logger = logging.getLogger(__name__)


def refresh_lastfm_track_stats(username, playlist_name):

    logger.info(f'refreshing {playlist_name} stats for {username}')

    fmnet = database.get_authed_lastfm_network(username=username)
    spotnet = database.get_authed_spotify_network(username=username)
    counter = Counter(fmnet=fmnet, spotnet=spotnet)

    database_ref = database.get_user_playlist_ref_by_username(user=username, playlist=playlist_name)

    playlist_dict = database_ref.get().to_dict()

    spotify_playlist = spotnet.get_playlist(uri=Uri(playlist_dict['uri']))
    track_count = counter.count_playlist(playlist=spotify_playlist)

    user_count = fmnet.get_user_scrobble_count()
    percent = round((track_count * 100) / user_count, 2)

    database_ref.update({
        'lastfm_stat_count': track_count,
        'lastfm_stat_percent': percent,

        'lastfm_stat_last_refresh': datetime.utcnow()
    })


def refresh_lastfm_album_stats(username, playlist_name):

    logger.info(f'refreshing {playlist_name} stats for {username}')

    fmnet = database.get_authed_lastfm_network(username=username)
    spotnet = database.get_authed_spotify_network(username=username)
    counter = Counter(fmnet=fmnet, spotnet=spotnet)

    database_ref = database.get_user_playlist_ref_by_username(user=username, playlist=playlist_name)

    playlist_dict = database_ref.get().to_dict()

    spotify_playlist = spotnet.get_playlist(uri=Uri(playlist_dict['uri']))
    album_count = counter.count_playlist(playlist=spotify_playlist, query_album=True)

    user_count = fmnet.get_user_scrobble_count()
    album_percent = round((album_count * 100) / user_count, 2)

    database_ref.update({
        'lastfm_stat_album_count': album_count,
        'lastfm_stat_album_percent': album_percent,

        'lastfm_stat_last_refresh': datetime.utcnow()
    })


def refresh_lastfm_artist_stats(username, playlist_name):

    logger.info(f'refreshing {playlist_name} stats for {username}')

    fmnet = database.get_authed_lastfm_network(username=username)
    spotnet = database.get_authed_spotify_network(username=username)
    counter = Counter(fmnet=fmnet, spotnet=spotnet)

    database_ref = database.get_user_playlist_ref_by_username(user=username, playlist=playlist_name)

    playlist_dict = database_ref.get().to_dict()

    spotify_playlist = spotnet.get_playlist(uri=Uri(playlist_dict['uri']))
    artist_count = counter.count_playlist(playlist=spotify_playlist, query_artist=True)

    user_count = fmnet.get_user_scrobble_count()
    artist_percent = round((artist_count * 100) / user_count, 2)

    database_ref.update({
        'lastfm_stat_artist_count': artist_count,
        'lastfm_stat_artist_percent': artist_percent,

        'lastfm_stat_last_refresh': datetime.utcnow()
    })
