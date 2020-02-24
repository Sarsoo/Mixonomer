from google.cloud import firestore
import logging
from datetime import timedelta, datetime, timezone
from typing import List, Optional
from werkzeug.security import generate_password_hash

from spotframework.net.network import Network as SpotifyNetwork
from fmframework.net.network import Network as FmNetwork
from music.db.user import DatabaseUser
from music.model.user import User
from music.model.playlist import Playlist, RecentsPlaylist, LastFMChartPlaylist, Sort
from music.model.tag import Tag

db = firestore.Client()

logger = logging.getLogger(__name__)


def refresh_token_database_callback(user):
    if isinstance(user, DatabaseUser):
        user_obj = get_user(user.user_id)

        user_obj.update_database({
            'access_token': user.access_token,
            'refresh_token': user.refresh_token,
            'last_refreshed': user.last_refreshed,
            'token_expiry': user.token_expiry
        })
        logger.debug(f'{user.user_id} database entry updated')
    else:
        logger.error('user has no attached id')


def get_authed_spotify_network(username):

    user = get_user(username)
    if user is not None:
        if user.spotify_linked:
            spotify_keys = db.document('key/spotify').get().to_dict()

            user_obj = DatabaseUser(client_id=spotify_keys['clientid'],
                                    client_secret=spotify_keys['clientsecret'],
                                    refresh_token=user.refresh_token,
                                    user_id=username,
                                    access_token=user.access_token)
            user_obj.on_refresh.append(refresh_token_database_callback)

            if user.last_refreshed + timedelta(seconds=user.token_expiry - 1) \
                    < datetime.now(timezone.utc):
                user_obj.refresh_access_token()

            user_obj.refresh_info()
            return SpotifyNetwork(user_obj)
        else:
            logger.error('user spotify not linked')
    else:
        logger.error(f'user {username} not found')


def get_authed_lastfm_network(username):

    user = get_user(username)
    if user:
        if user.lastfm_username:
            fm_keys = db.document('key/fm').get().to_dict()
            return FmNetwork(username=user.lastfm_username, api_key=fm_keys['clientid'])
        else:
            logger.error(f'{username} has no last.fm username')
    else:
        logger.error(f'user {username} not found')


def get_users() -> List[User]:
    logger.info('retrieving users')
    return [parse_user_reference(user_snapshot=i) for i in db.collection(u'spotify_users').stream()]


def get_user(username: str) -> Optional[User]:
    logger.info(f'retrieving {username}')

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', username).stream()]

    if len(users) == 0:
        logger.error(f'user {username} not found')
        return None
    if len(users) > 1:
        logger.critical(f"multiple {username}'s found")
        return None

    return parse_user_reference(user_snapshot=users[0])


def parse_user_reference(user_ref=None, user_snapshot=None) -> User:
    if user_ref is None and user_snapshot is None:
        raise ValueError('no user object supplied')

    if user_ref is None:
        user_ref = user_snapshot.reference

    if user_snapshot is None:
        user_snapshot = user_ref.get()

    user_dict = user_snapshot.to_dict()

    return User(username=user_dict.get('username'),
                password=user_dict.get('password'),
                db_ref=user_ref,
                email=user_dict.get('email'),
                user_type=User.Type[user_dict.get('type')],
                last_login=user_dict.get('last_login'),
                last_refreshed=user_dict.get('last_refreshed'),
                locked=user_dict.get('locked'),
                validated=user_dict.get('validated'),

                spotify_linked=user_dict.get('spotify_linked'),
                access_token=user_dict.get('access_token'),
                refresh_token=user_dict.get('refresh_token'),
                token_expiry=user_dict.get('token_expiry'),
                lastfm_username=user_dict.get('lastfm_username'))


def update_user(username: str, updates: dict) -> None:
    logger.debug(f'updating {username}')

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', username).stream()]

    if len(users) == 0:
        logger.error(f'user {username} not found')
        return None
    if len(users) > 1:
        logger.critical(f"multiple {username}'s found")
        return None

    user = users[0].reference
    user.update(updates)


def create_user(username: str, password: str):
    db.collection(u'spotify_users').add({
        'access_token': None,
        'email': None,
        'last_login': datetime.utcnow(),
        'last_refreshed': None,
        'locked': False,
        'password': generate_password_hash(password),
        'refresh_token': None,
        'spotify_linked': False,
        'type': 'user',
        'username': username,
        'validated': True
    })


def get_user_playlists(username: str) -> List[Playlist]:
    logger.info(f'getting playlists for {username}')

    user = get_user(username)

    if user:
        playlist_refs = [i for i in user.db_ref.collection(u'playlists').stream()]

        return [parse_playlist_reference(username=username, playlist_snapshot=i) for i in playlist_refs]
    else:
        logger.error(f'user {username} not found')


def get_playlist(username: str = None, name: str = None) -> Optional[Playlist]:
    logger.info(f'retrieving {name} for {username}')

    user = get_user(username)

    if user:

        playlists = [i for i in user.db_ref.collection(u'playlists').where(u'name', u'==', name).stream()]

        if len(playlists) == 0:
            logger.error(f'playlist {name} for {user} not found')
            return None
        if len(playlists) > 1:
            logger.critical(f"multiple {name}'s for {user} found")
            return None

        return parse_playlist_reference(username=username, playlist_snapshot=playlists[0])
    else:
        logger.error(f'user {username} not found')


def parse_playlist_reference(username, playlist_ref=None, playlist_snapshot=None) -> Playlist:
    if playlist_ref is None and playlist_snapshot is None:
        raise ValueError('no playlist object supplied')

    if playlist_ref is None:
        playlist_ref = playlist_snapshot.reference

    if playlist_snapshot is None:
        playlist_snapshot = playlist_ref.get()

    playlist_dict = playlist_snapshot.to_dict()

    if playlist_dict.get('type') == 'default':
        return Playlist(uri=playlist_dict.get('uri'),
                        name=playlist_dict.get('name'),
                        username=username,

                        db_ref=playlist_ref,

                        include_recommendations=playlist_dict.get('include_recommendations', False),
                        recommendation_sample=playlist_dict.get('recommendation_sample', 0),
                        include_library_tracks=playlist_dict.get('include_library_tracks', False),

                        parts=playlist_dict.get('parts'),
                        playlist_references=playlist_dict.get('playlist_references'),
                        shuffle=playlist_dict.get('shuffle'),

                        sort=Sort[playlist_dict.get('sort', 'release_date')],

                        description_overwrite=playlist_dict.get('description_overwrite'),
                        description_suffix=playlist_dict.get('description_suffix'),

                        last_updated=playlist_dict.get('last_updated'),

                        lastfm_stat_count=playlist_dict.get('lastfm_stat_count', 0),
                        lastfm_stat_album_count=playlist_dict.get('lastfm_stat_album_count', 0),
                        lastfm_stat_artist_count=playlist_dict.get('lastfm_stat_artist_count', 0),

                        lastfm_stat_percent=playlist_dict.get('lastfm_stat_percent', 0),
                        lastfm_stat_album_percent=playlist_dict.get('lastfm_stat_album_percent', 0),
                        lastfm_stat_artist_percent=playlist_dict.get('lastfm_stat_artist_percent', 0),

                        lastfm_stat_last_refresh=playlist_dict.get('lastfm_stat_last_refresh'))

    elif playlist_dict.get('type') == 'recents':
        return RecentsPlaylist(uri=playlist_dict.get('uri'),
                               name=playlist_dict.get('name'),
                               username=username,

                               db_ref=playlist_ref,

                               include_recommendations=playlist_dict.get('include_recommendations', False),
                               recommendation_sample=playlist_dict.get('recommendation_sample', 0),
                               include_library_tracks=playlist_dict.get('include_library_tracks', False),

                               parts=playlist_dict.get('parts'),
                               playlist_references=playlist_dict.get('playlist_references'),
                               shuffle=playlist_dict.get('shuffle'),

                               sort=Sort[playlist_dict.get('sort', 'release_date')],

                               description_overwrite=playlist_dict.get('description_overwrite'),
                               description_suffix=playlist_dict.get('description_suffix'),

                               last_updated=playlist_dict.get('last_updated'),

                               lastfm_stat_count=playlist_dict.get('lastfm_stat_count', 0),
                               lastfm_stat_album_count=playlist_dict.get('lastfm_stat_album_count', 0),
                               lastfm_stat_artist_count=playlist_dict.get('lastfm_stat_artist_count', 0),

                               lastfm_stat_percent=playlist_dict.get('lastfm_stat_percent', 0),
                               lastfm_stat_album_percent=playlist_dict.get('lastfm_stat_album_percent', 0),
                               lastfm_stat_artist_percent=playlist_dict.get('lastfm_stat_artist_percent', 0),

                               lastfm_stat_last_refresh=playlist_dict.get('lastfm_stat_last_refresh'),

                               add_last_month=playlist_dict.get('add_last_month'),
                               add_this_month=playlist_dict.get('add_this_month'),
                               day_boundary=playlist_dict.get('day_boundary'))

    elif playlist_dict.get('type') == 'fmchart':
        return LastFMChartPlaylist(uri=playlist_dict.get('uri'),
                                   name=playlist_dict.get('name'),
                                   username=username,

                                   db_ref=playlist_ref,

                                   include_recommendations=playlist_dict.get('include_recommendations', False),
                                   recommendation_sample=playlist_dict.get('recommendation_sample', 0),
                                   include_library_tracks=playlist_dict.get('include_library_tracks', False),

                                   parts=playlist_dict.get('parts'),
                                   playlist_references=playlist_dict.get('playlist_references'),
                                   shuffle=playlist_dict.get('shuffle'),

                                   sort=Sort[playlist_dict.get('sort', 'release_date')],

                                   description_overwrite=playlist_dict.get('description_overwrite'),
                                   description_suffix=playlist_dict.get('description_suffix'),

                                   last_updated=playlist_dict.get('last_updated'),

                                   lastfm_stat_count=playlist_dict.get('lastfm_stat_count', 0),
                                   lastfm_stat_album_count=playlist_dict.get('lastfm_stat_album_count', 0),
                                   lastfm_stat_artist_count=playlist_dict.get('lastfm_stat_artist_count', 0),

                                   lastfm_stat_percent=playlist_dict.get('lastfm_stat_percent', 0),
                                   lastfm_stat_album_percent=playlist_dict.get('lastfm_stat_album_percent', 0),
                                   lastfm_stat_artist_percent=playlist_dict.get('lastfm_stat_artist_percent', 0),

                                   lastfm_stat_last_refresh=playlist_dict.get('lastfm_stat_last_refresh'),

                                   chart_limit=playlist_dict.get('chart_limit'),
                                   chart_range=FmNetwork.Range[playlist_dict.get('chart_range')])


def update_playlist(username: str, name: str, updates: dict) -> None:
    if len(updates) > 0:
        logger.debug(f'updating {name} for {username}')

        user = get_user(username)

        playlists = [i for i in user.db_ref.collection(u'playlists').where(u'name', u'==', name).stream()]

        if len(playlists) == 0:
            logger.error(f'playlist {name} for {username} not found')
            return None
        if len(playlists) > 1:
            logger.critical(f"multiple {name}'s for {username} found")
            return None

        playlist = playlists[0].reference
        playlist.update(updates)
    else:
        logger.debug(f'nothing to update for {name} for {username}')


def delete_playlist(username: str, name: str) -> None:
    logger.info(f'deleting {name} for {username}')

    playlist = get_playlist(username=username, name=name)

    if playlist:
        playlist.db_ref.delete()
    else:
        logger.error(f'playlist {name} not found for {username}')


def get_user_tags(username: str) -> List[Tag]:
    logger.info(f'getting tags for {username}')

    user = get_user(username)

    if user:
        tag_refs = [i for i in user.db_ref.collection(u'tags').stream()]

        return [parse_tag_reference(username=username, tag_snapshot=i) for i in tag_refs]
    else:
        logger.error(f'user {username} not found')


def get_tag(username: str = None, tag_id: str = None) -> Optional[Tag]:
    logger.info(f'retrieving {tag_id} for {username}')

    user = get_user(username)

    if user:

        tags = [i for i in user.db_ref.collection(u'tags').where(u'tag_id', u'==', tag_id).stream()]

        if len(tags) == 0:
            logger.error(f'tag {tag_id} for {user} not found')
            return None
        if len(tags) > 1:
            logger.critical(f"multiple {tag_id}'s for {user} found")
            return None

        return parse_tag_reference(username=username, tag_snapshot=tags[0])
    else:
        logger.error(f'user {username} not found')


def parse_tag_reference(username, tag_ref=None, tag_snapshot=None) -> Tag:
    if tag_ref is None and tag_snapshot is None:
        raise ValueError('no tag object supplied')

    if tag_ref is None:
        tag_ref = tag_snapshot.reference

    if tag_snapshot is None:
        tag_snapshot = tag_ref.get()

    tag_dict = tag_snapshot.to_dict()

    return Tag(tag_id=tag_dict['tag_id'],
               name=tag_dict.get('name', 'n/a'),
               username=username,

               db_ref=tag_ref,

               tracks=tag_dict.get('tracks', []),
               albums=tag_dict.get('albums', []),
               artists=tag_dict.get('artists', []),

               count=tag_dict.get('count', 0),
               proportion=tag_dict.get('proportion', 0.0),
               total_user_scrobbles=tag_dict.get('total_user_scrobbles', 0),

               last_updated=tag_dict.get('last_updated'))


def update_tag(username: str, tag_id: str, updates: dict) -> None:
    if len(updates) > 0:
        logger.debug(f'updating {tag_id} for {username}')

        user = get_user(username)

        tags = [i for i in user.db_ref.collection(u'tags').where(u'tag_id', u'==', tag_id).stream()]

        if len(tags) == 0:
            logger.error(f'tag {tag_id} for {username} not found')
            return None
        if len(tags) > 1:
            logger.critical(f"multiple {tag_id}'s for {username} found")
            return None

        tag = tags[0].reference
        tag.update(updates)
    else:
        logger.debug(f'nothing to update for {tag_id} for {username}')


def delete_tag(username: str, tag_id: str) -> bool:
    logger.info(f'deleting {tag_id} for {username}')

    tag = get_tag(username=username, tag_id=tag_id)

    if tag:
        tag.db_ref.delete()
        return True
    else:
        logger.error(f'playlist {tag_id} not found for {username}')
        return False


def create_tag(username: str, tag_id: str):
    user = get_user(username)

    if user is None:
        logger.error(f'{username} not found')
        return None

    if tag_id in [i.tag_id for i in get_user_tags(username)]:
        logger.error(f'{tag_id} already exists for {username}')
        return None

    user.db_ref.collection(u'tags').add({
        'tag_id': tag_id,
        'name': tag_id,

        'tracks': [],
        'albums': [],
        'artists': [],

        'count': 0,
        'proportion': 0.0,
        'total_user_scrobbles': 0,
        'last_updated': None
    })
