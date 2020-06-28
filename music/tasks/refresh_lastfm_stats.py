from google.cloud import firestore

import logging
from datetime import datetime

import music.db.database as database
from music.model.user import User
from music.model.playlist import Playlist

from spotfm.maths.counter import Counter
from spotframework.model.uri import Uri
from spotframework.net.network import SpotifyNetworkException

from fmframework.net.network import LastFMNetworkException

db = firestore.Client()

logger = logging.getLogger(__name__)


def refresh_lastfm_track_stats(username, playlist_name):

    logger.info(f'refreshing {playlist_name} stats for {username}')

    user = User.collection.filter('username', '==', username.strip().lower()).get()
    if user is None:
        logger.error(f'user {username} not found')

    fmnet = database.get_authed_lastfm_network(user)
    spotnet = database.get_authed_spotify_network(user)
    counter = Counter(fmnet=fmnet, spotnet=spotnet)

    playlist = Playlist.collection.parent(user.key).filter('name', '==', playlist_name).get()

    if playlist is None:
        logger.critical(f'playlist {playlist_name} for {username} not found')
        return

    if playlist.uri is None:
        logger.critical(f'playlist {playlist_name} for {username} has no spotify uri')
        return

    try:
        spotify_playlist = spotnet.get_playlist(uri=Uri(playlist.uri))
    except SpotifyNetworkException as e:
        logger.error(f'error retrieving spotify playlist {username} / {playlist_name} - {e}')
        return
    track_count = counter.count_playlist(playlist=spotify_playlist)

    try:
        user_count = fmnet.get_user_scrobble_count()
        if user_count > 0:
            percent = round((track_count * 100) / user_count, 2)
        else:
            percent = 0
    except LastFMNetworkException as e:
        logger.error(f'error while retrieving user scrobble count - {e}')
        percent = 0

    playlist.lastfm_stat_count = track_count
    playlist.lastfm_stat_percent = percent
    playlist.lastfm_stat_last_refresh = datetime.utcnow()

    playlist.update()


def refresh_lastfm_album_stats(username, playlist_name):

    logger.info(f'refreshing {playlist_name} stats for {username}')

    user = User.collection.filter('username', '==', username.strip().lower()).get()
    if user is None:
        logger.error(f'user {username} not found')

    fmnet = database.get_authed_lastfm_network(user)
    spotnet = database.get_authed_spotify_network(user)
    counter = Counter(fmnet=fmnet, spotnet=spotnet)

    playlist = Playlist.collection.parent(user.key).filter('name', '==', playlist_name).get()

    if playlist is None:
        logger.critical(f'playlist {playlist_name} for {username} not found')
        return

    if playlist.uri is None:
        logger.critical(f'playlist {playlist_name} for {username} has no spotify uri')
        return

    try:
        spotify_playlist = spotnet.get_playlist(uri=Uri(playlist.uri))
    except SpotifyNetworkException as e:
        logger.error(f'error retrieving spotify playlist {username} / {playlist_name} - {e}')
        return
    album_count = counter.count_playlist(playlist=spotify_playlist, query_album=True)

    try:
        user_count = fmnet.get_user_scrobble_count()
        if user_count > 0:
            album_percent = round((album_count * 100) / user_count, 2)
        else:
            album_percent = 0
    except LastFMNetworkException as e:
        logger.error(f'error while retrieving user scrobble count - {e}')
        album_percent = 0

    playlist.lastfm_stat_album_count = album_count
    playlist.lastfm_stat_album_percent = album_percent
    playlist.lastfm_stat_last_refresh = datetime.utcnow()

    playlist.update()


def refresh_lastfm_artist_stats(username, playlist_name):

    logger.info(f'refreshing {playlist_name} stats for {username}')

    user = User.collection.filter('username', '==', username.strip().lower()).get()
    if user is None:
        logger.error(f'user {username} not found')

    fmnet = database.get_authed_lastfm_network(user)
    spotnet = database.get_authed_spotify_network(user)
    counter = Counter(fmnet=fmnet, spotnet=spotnet)

    playlist = Playlist.collection.parent(user.key).filter('name', '==', playlist_name).get()

    if playlist is None:
        logger.critical(f'playlist {playlist_name} for {username} not found')
        return

    if playlist.uri is None:
        logger.critical(f'playlist {playlist_name} for {username} has no spotify uri')
        return

    try:
        spotify_playlist = spotnet.get_playlist(uri=Uri(playlist.uri))
    except SpotifyNetworkException as e:
        logger.error(f'error retrieving spotify playlist {username} / {playlist_name} - {e}')
        return
    artist_count = counter.count_playlist(playlist=spotify_playlist, query_artist=True)

    try:
        user_count = fmnet.get_user_scrobble_count()
        if user_count > 0:
            artist_percent = round((artist_count * 100) / user_count, 2)
        else:
            artist_percent = 0
    except LastFMNetworkException as e:
        logger.error(f'error while retrieving user scrobble count - {e}')
        artist_percent = 0

    playlist.lastfm_stat_artist_count = artist_count
    playlist.lastfm_stat_artist_percent = artist_percent
    playlist.lastfm_stat_last_refresh = datetime.utcnow()

    playlist.update()
