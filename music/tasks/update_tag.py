import logging
from datetime import datetime

import music.db.database as database

logger = logging.getLogger(__name__)


def update_tag(username, tag_id):
    logger.info(f'updating {username} / {tag_id}')

    tag = database.get_tag(username=username, tag_id=tag_id)

    if tag is None:
        logger.error(f'{tag_id} for {username} not found')
        return

    user = database.get_user(username)

    if user.lastfm_username is None or len(user.lastfm_username) == 0:
        logger.error(f'{username} has no last.fm username')
        return

    net = database.get_authed_lastfm_network(username=username)

    tag_count = 0
    user_scrobbles = net.get_user_scrobble_count()

    artists = []
    for artist in tag.artists:
        net_artist = net.get_artist(name=artist['name'])

        if net_artist is not None:
            artist['count'] = net_artist.user_scrobbles
            tag_count += net_artist.user_scrobbles

        artists.append(artist)

    albums = []
    for album in tag.albums:
        net_album = net.get_album(name=album['name'], artist=album['artist'])

        if net_album is not None:
            album['count'] = net_album.user_scrobbles

            if album['artist'].lower() not in [i.lower() for i in [j['name'] for j in artists]]:
                tag_count += net_album.user_scrobbles

        albums.append(album)

    tracks = []
    for track in tag.tracks:
        net_track = net.get_track(name=track['name'], artist=track['artist'])

        if net_track is not None:
            track['count'] = net_track.user_scrobbles

            if track['artist'].lower() not in [i.lower() for i in [j['name'] for j in artists]]:
                tag_count += net_track.user_scrobbles

        tracks.append(track)

    tag.update_database({
        'tracks': tracks,
        'albums': albums,
        'artists': artists,

        'total_user_scrobbles': user_scrobbles,
        'count': tag_count,
        'proportion': (tag_count / user_scrobbles) * 100,
        'last_updated': datetime.utcnow()
    })
