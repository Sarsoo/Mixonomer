import datetime
import logging
import random
from typing import List

import spotframework.util.monthstrings as monthstrings
from spotframework.model.uri import Uri
from spotframework.filter import remove_local, get_track_objects
from spotframework.filter.added import added_after
from spotframework.filter.sort import sort_by_release_date
from spotframework.filter.deduplicate import deduplicate_by_name
from spotframework.net.network import SpotifyNetworkException

from spotframework.net.network import Network as SpotNetwork
from fmframework.net.network import Network
from spotfm.chart import map_lastfm_track_chart_to_spotify

import music.db.database as database
from music.db.part_generator import PartGenerator
from music.model.user import User
from music.model.playlist import Playlist

from music.notif.notifier import notify_user_playlist_update

logger = logging.getLogger(__name__)


def get_user_and_name(user):
    if isinstance(user, str):
        username = user
        user = User.collection.filter('username', '==', username.strip().lower()).get()

        return user, username
    else:
        return user, user.username


def get_playlist_and_name(playlist, user: User):
    if isinstance(playlist, str):
        playlist_name = playlist
        playlist = user.get_playlist(playlist_name)

        return playlist, playlist_name

    else:
        return playlist, playlist.name


def run_user_playlist(user: User, playlist: Playlist, spotnet: SpotNetwork = None, fmnet: Network = None) -> None:
    """Generate and upadate a user's smart playlist

    Args:
        user (User): Subject user
        playlist (Playlist): User's subject playlist
        spotnet (SpotNetwork, optional): Spotframework network for Spotify operations. Defaults to None.
        fmnet (Network, optional): Fmframework network for Last.fm operations. Defaults to None.

    Raises:
        NameError: No user provided
        NameError: No playlist provided
        AttributeError: Playlist has no URI
        NameError: No spotframework network available
        e: spotframework error when retrieving user playlists

    Returns:
        [type]: [description]
    """

    # PRE-RUN CHECKS

    user, username = get_user_and_name(user)

    if user is None:
        logger.error(f'user {username} not found')
        raise NameError(f'User {username} not found')

    playlist, playlist_name = get_playlist_and_name(playlist, user)

    if playlist.uri is None:
        logger.critical(f'no playlist id to populate {username} / {playlist_name}')
        raise AttributeError(f'No URI for {playlist_name} ({username})')

    # END CHECKS

    logger.info(f'running {username} / {playlist_name}')

    if spotnet is None:
        spotnet = database.get_authed_spotify_network(user)

    if spotnet is None:
        logger.error(f'no spotify network returned for {username} / {playlist_name}')
        raise NameError(f'No Spotify network returned ({username} / {playlist_name})')

    part_generator = PartGenerator(user=user)
    part_names = part_generator.get_recursive_parts(playlist.name)

    playlist_tracks = load_playlist_tracks(spotnet, playlist, part_names, username)
    playlist_tracks = do_playlist_type_processing(spotnet, playlist, user, playlist_tracks)
    playlist_tracks = sort_tracks(playlist, playlist_tracks)
    playlist_tracks += get_recommendations(spotnet, playlist, username, playlist_tracks)
    playlist_tracks = deduplicate_by_name(playlist_tracks)

    execute_playlist(spotnet, playlist, part_names, username, playlist_tracks)

    playlist.last_updated = datetime.datetime.utcnow()
    playlist.update()

    notify_user_playlist_update(user=user, playlist=playlist)

def load_user_playlists(spotnet: SpotNetwork, playlist: Playlist, username: str):
    try:
        if not playlist.include_spotify_owned:
            return {i.name: i.uri
                    for i in spotnet.playlists()
                    if 'spotify' not in i.owner.display_name.lower()}
        else:
            return {i.name: i.uri
                    for i in spotnet.playlists()}
    except SpotifyNetworkException as e:
        logger.exception(f'error occured while retrieving playlists {username} / {playlist.name}')
        raise e

def load_playlist_tracks(spotnet: SpotNetwork, playlist: Playlist, part_names: List[str], username: str):
    playlist_tracks = []

    if playlist.add_last_month:
        part_names.append(monthstrings.get_last_month())
    if playlist.add_this_month:
        part_names.append(monthstrings.get_this_month())

    user_playlists = load_user_playlists(spotnet, playlist, username)

    #  LOAD PLAYLIST TRACKS
    for part_name in part_names:
        try:  # attempt to cast to uri
            uri = Uri(part_name)
            log_name = uri

        except ValueError:  # is a playlist name
            uri = user_playlists.get(part_name)
            if uri is None:
                logger.warning(f'playlist {part_name} not found {username} / {playlist.name}')
                continue

            log_name = part_name

        try:
            _tracks = spotnet.playlist_tracks(uri=uri, reduced_mem=True)
            if _tracks and len(_tracks) > 0:
                playlist_tracks += _tracks
            else:
                logger.warning(f'no tracks returned for {log_name} {username} / {playlist.name}')
        except SpotifyNetworkException:
            logger.exception(f'error occured while retrieving {log_name} {username} / {playlist.name}')

    playlist_tracks = list(remove_local(playlist_tracks))

    playlist_tracks += load_library_tracks(spotnet, playlist, username)

    return playlist_tracks

def load_library_tracks(spotnet: SpotNetwork, playlist: Playlist, username: str):
    tracks = []

    if playlist.include_library_tracks:
        try:
            library_tracks = spotnet.saved_tracks()
            if library_tracks and len(library_tracks) > 0:
                tracks += library_tracks
            else:
                logger.error(f'error getting library tracks {username} / {playlist.name}')
        except SpotifyNetworkException:
            logger.exception(f'error occured while retrieving library tracks {username} / {playlist.name}')

    return tracks

def do_playlist_type_processing(spotnet: SpotNetwork, playlist: Playlist, user: User, current_tracks: List):
    if playlist.type == 'recents':
        return do_recents_processing(playlist, current_tracks)
    elif playlist.type == 'fmchart':
        return do_lastfm_chart_processing(spotnet, playlist, user, current_tracks)
    return current_tracks

def do_recents_processing(playlist: Playlist, current_tracks: List):
    boundary_date = datetime.datetime.now(datetime.timezone.utc) - \
                    datetime.timedelta(days=int(playlist.day_boundary))
    return list(added_after(current_tracks, boundary_date))

def do_lastfm_chart_processing(spotnet: SpotNetwork, playlist: Playlist, user: User, current_tracks: List):
    if user.lastfm_username is None:
        logger.error(f'no associated last.fm username, chart source skipped {user.username} / {playlist.name}')
    else:
        chart_range = Network.Range.MONTH
        try:
            chart_range = Network.Range[playlist.chart_range]
        except KeyError:
            logger.error(f'invalid last.fm chart range found {playlist.chart_range}, '
                         f'defaulting to 1 month {user.username} / {playlist.name}')

        fmnet = database.get_authed_lastfm_network(user)

        if fmnet is not None:
            chart_tracks = map_lastfm_track_chart_to_spotify(spotnet=spotnet,
                                                             fmnet=fmnet,
                                                             period=chart_range,
                                                             limit=playlist.chart_limit)

            if chart_tracks is not None and len(chart_tracks) > 0:
                current_tracks += chart_tracks
            else:
                logger.error(f'no tracks returned {user.username} / {playlist.name}')
        else:
            logger.error(f'no last.fm network returned {user.username} / {playlist.name}')

    return current_tracks

def sort_tracks(playlist: Playlist, current_tracks: List):
    if playlist.shuffle:
        random.shuffle(current_tracks)
        return current_tracks
    elif playlist.type != 'fmchart':
        return sort_by_release_date(tracks=current_tracks, reverse=True)
    return current_tracks

def get_recommendations(spotnet: SpotNetwork, playlist: Playlist, username: str, current_tracks: List):

    recommendations = []

    if playlist.include_recommendations:
        try:
            recommendations = spotnet.recommendations(tracks=[i.uri.object_id for i, j
                                                              in get_track_objects(
                    random.sample(current_tracks,
                                  k=min(5, len(current_tracks))
                                  )
                )
                                                              if i.uri.object_type == Uri.ObjectType.track],
                                                      response_limit=playlist.recommendation_sample)
            if recommendations and len(recommendations.tracks) > 0:
                recommendations = recommendations.tracks
            else:
                logger.error(f'error getting recommendations {username} / {playlist.name}')
        except SpotifyNetworkException:
            logger.exception(f'error occured while generating recommendations {username} / {playlist.name}')

    return recommendations

def execute_playlist(spotnet: SpotNetwork, playlist: Playlist, part_names, username: str, current_tracks: List):
    try:
        spotnet.replace_playlist_tracks(uri=playlist.uri, uris=[i.uri for i, j in get_track_objects(current_tracks)])

        if playlist.description_overwrite:
            string = playlist.description_overwrite
        else:
            string = ' / '.join(sorted(part_names))

        if playlist.description_suffix:
            string += f' - {str(playlist.description_suffix)}'

        if string is None or len(string) == 0:
            logger.error(f'no string generated {username} / {playlist.name}')
            return None

        try:
            spotnet.change_playlist_details(uri=playlist.uri, description=string)
        except SpotifyNetworkException:
            logger.exception(f'error changing description for {username} / {playlist.name}')

    except SpotifyNetworkException:
        logger.exception(f'error executing {username} / {playlist.name}')