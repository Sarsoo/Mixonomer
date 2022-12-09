import logging
from datetime import datetime

import music.db.database as database
from music.model.user import User
from music.model.tag import Tag
from music.notif.notifier import notify_user_tag_update

from fmframework.net.network import LastFMNetworkException

from spotfm.timer import time, seconds_to_time_str

logger = logging.getLogger(__name__)


def update_tag(user: User, tag: Tag, spotnet=None, fmnet=None):

    # PRE-RUN CHECKS

    if isinstance(user, str):
        username = user
        user = User.collection.filter('username', '==', username.strip().lower()).get()
    else:
        username = user.username

    if user is None:
        logger.error(f'user {username} not found')
        raise NameError(f'User {username} not found')

    if isinstance(tag, str):
        tag_id = tag
        tag = Tag.collection.parent(user.key).filter('tag_id', '==', tag_id).get()
    else:
        tag_id = tag.tag_id
    
    if tag is None:
        logger.error(f'{tag_id} for {username} not found')
        raise NameError(f'Tag {tag_id} not found for {username}')

    if user.lastfm_username is None or len(user.lastfm_username) == 0:
        logger.error(f'{username} has no last.fm username')
        raise AttributeError(f'{username} has no Last.fm username ({tag_id})')

    # END CHECKS

    logger.info(f'updating {username} / {tag_id}')

    if fmnet is None:
        fmnet = database.get_authed_lastfm_network(user)
    
    if fmnet is None:
        logger.error(f'no last.fm network returned for {username} / {tag_id}')
        raise NameError(f'No Last.fm network returned ({username} / {tag_id})')

    if tag.time_objects:
        if user.spotify_linked:
            if spotnet is None:
                spotnet = database.get_authed_spotify_network(user)
        else:
            logger.warning(f'timing objects requested but no spotify linked {username} / {tag_id}')

    tag.count = 0
    tag.total_time_ms = 0

    artists = []
    for artist in tag.artists:
        try:
            if tag.time_objects and user.spotify_linked:
                total_ms, timed_tracks = time(spotnet=spotnet, fmnet=fmnet,
                                              artist=artist['name'], username=user.lastfm_username,
                                              return_tracks=True)
                scrobbles = sum(i[0].user_scrobbles for i in timed_tracks)

                artist['time_ms'] = total_ms
                artist['time'] = seconds_to_time_str(milliseconds=total_ms)
                tag.total_time_ms += total_ms

            else:
                net_artist = fmnet.artist(name=artist['name'])

                if net_artist is not None:
                    scrobbles = net_artist.user_scrobbles
                else:
                    scrobbles = 0

            artist['count'] = scrobbles
            tag.count += scrobbles
        except LastFMNetworkException:
            logger.exception(f'error during artist retrieval {username} / {tag_id}')

        artists.append(artist)

    albums = []
    for album in tag.albums:
        try:
            if tag.time_objects and user.spotify_linked:
                total_ms, timed_tracks = time(spotnet=spotnet, fmnet=fmnet,
                                              album=album['name'], artist=album['artist'],
                                              username=user.lastfm_username, return_tracks=True)
                scrobbles = sum(i[0].user_scrobbles for i in timed_tracks)

                album['time_ms'] = total_ms
                album['time'] = seconds_to_time_str(milliseconds=total_ms)
                tag.total_time_ms += total_ms

            else:
                net_album = fmnet.album(name=album['name'], artist=album['artist'])

                if net_album is not None:
                    scrobbles = net_album.user_scrobbles
                else:
                    scrobbles = 0

            album['count'] = scrobbles

            if album['artist'].lower() not in [i.lower() for i in [j['name'] for j in artists]]:
                tag.count += scrobbles
        except LastFMNetworkException:
            logger.exception(f'error during album retrieval {username} / {tag_id}')

        albums.append(album)

    tracks = []
    for track in tag.tracks:
        try:
            if tag.time_objects and user.spotify_linked:
                total_ms, timed_tracks = time(spotnet=spotnet, fmnet=fmnet,
                                              track=track['name'], artist=track['artist'],
                                              username=user.lastfm_username, return_tracks=True)
                scrobbles = sum(i[0].user_scrobbles for i in timed_tracks)

                track['time_ms'] = total_ms
                track['time'] = seconds_to_time_str(milliseconds=total_ms)
                tag.total_time_ms += total_ms

            else:
                net_track = fmnet.track(name=track['name'], artist=track['artist'])

                if net_track is not None:
                    scrobbles = net_track.user_scrobbles
                else:
                    scrobbles = 0

            track['count'] = scrobbles

            if track['artist'].lower() not in [i.lower() for i in [j['name'] for j in artists]]:
                tag.count += scrobbles
        except LastFMNetworkException:
            logger.exception(f'error during track retrieval {username} / {tag_id}')

        tracks.append(track)

    tag.tracks = tracks
    tag.albums = albums
    tag.artists = artists

    tag.total_time = seconds_to_time_str(milliseconds=tag.total_time_ms)

    try:
        user_scrobbles = fmnet.user_scrobble_count()
    except LastFMNetworkException:
        logger.exception(f'error retrieving scrobble count {username} / {tag_id}')
        user_scrobbles = 0

    if user_scrobbles > 0:
        tag.total_user_scrobbles = user_scrobbles
        tag.proportion = (tag.count / user_scrobbles) * 100
    else:
        logger.warning(f'user scrobble count for {username} returned 0')
        tag.total_user_scrobbles = 0
        tag.proportion = 0

    tag.last_updated = datetime.utcnow()

    tag.update()

    notify_user_tag_update(user=user, tag=tag)
