import logging
from datetime import datetime

import music.db.database as database
from music.model.user import User
from music.model.tag import Tag

from fmframework.net.network import LastFMNetworkException

logger = logging.getLogger(__name__)


def update_tag(username, tag_id):
    logger.info(f'updating {username} / {tag_id}')

    user = User.collection.filter('username', '==', username.strip().lower()).get()
    if user is None:
        logger.error(f'user {username} not found')
        return

    tag = Tag.collection.parent(user.key).filter('tag_id', '==', tag_id).get()

    if tag is None:
        logger.error(f'{tag_id} for {username} not found')
        return

    if user.lastfm_username is None or len(user.lastfm_username) == 0:
        logger.error(f'{username} has no last.fm username')
        return

    net = database.get_authed_lastfm_network(user)

    if net is None:
        logger.error(f'no last.fm network returned for {username}')
        return

    tag_count = 0
    try:
        user_scrobbles = net.get_user_scrobble_count()
    except LastFMNetworkException:
        logger.exception(f'error retrieving scrobble count {username} / {tag_id}')
        user_scrobbles = 0

    artists = []
    for artist in tag.artists:
        try:
            net_artist = net.get_artist(name=artist['name'])

            if net_artist is not None:
                artist['count'] = net_artist.user_scrobbles
                tag_count += net_artist.user_scrobbles
        except LastFMNetworkException:
            logger.exception(f'error during artist retrieval {username} / {tag_id}')

        artists.append(artist)

    albums = []
    for album in tag.albums:
        try:
            net_album = net.get_album(name=album['name'], artist=album['artist'])

            if net_album is not None:
                album['count'] = net_album.user_scrobbles

                if album['artist'].lower() not in [i.lower() for i in [j['name'] for j in artists]]:
                    tag_count += net_album.user_scrobbles
        except LastFMNetworkException:
            logger.exception(f'error during album retrieval {username} / {tag_id}')

        albums.append(album)

    tracks = []
    for track in tag.tracks:
        try:
            net_track = net.get_track(name=track['name'], artist=track['artist'])

            if net_track is not None:
                track['count'] = net_track.user_scrobbles

                if track['artist'].lower() not in [i.lower() for i in [j['name'] for j in artists]]:
                    tag_count += net_track.user_scrobbles
        except LastFMNetworkException:
            logger.exception(f'error during track retrieval {username} / {tag_id}')

        tracks.append(track)

    tag.tracks = tracks
    tag.albums = albums
    tag.artists = artists

    tag.total_user_scrobbles = user_scrobbles
    tag.count = tag_count
    tag.proportion = (tag_count / user_scrobbles) * 100
    tag.last_updated = datetime.utcnow()

    tag.update()
