import datetime
import logging
import random

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

logger = logging.getLogger(__name__)


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

    if isinstance(user, str):
        username = user
        user = User.collection.filter('username', '==', username.strip().lower()).get()
    else:
        username = user.username

    if user is None:
        logger.error(f'user {username} not found')
        raise NameError(f'User {username} not found')

    if isinstance(playlist, str):
        playlist_name = playlist
        playlist = user.get_playlist(playlist_name)

    else:
        playlist_name = playlist.name 

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

    try:
        if not playlist.include_spotify_owned:
            user_playlists = {i.name: i.uri for i in spotnet.playlists() if 'spotify' not in i.owner.display_name.lower()}
        else:
            user_playlists = {i.name: i.uri for i in spotnet.playlists()}
    except SpotifyNetworkException as e:
        logger.exception(f'error occured while retrieving playlists {username} / {playlist_name}')
        raise e

    part_generator = PartGenerator(user=user)
    part_names = part_generator.get_recursive_parts(playlist.name)

    playlist_tracks = []

    if playlist.add_last_month:
        part_names.append(monthstrings.get_last_month())
    if playlist.add_this_month:
        part_names.append(monthstrings.get_this_month())

    #  LOAD PLAYLIST TRACKS
    for part_name in part_names:
        try:  # attempt to cast to uri
            uri = Uri(part_name)
            log_name = uri

        except ValueError:  # is a playlist name
            uri = user_playlists.get(part_name)
            if uri is None:
                logger.warning(f'playlist {part_name} not found {username} / {playlist_name}')
                continue
            
            log_name = part_name

        try:
            _tracks = spotnet.playlist_tracks(uri=uri, reduced_mem=True)
            if _tracks and len(_tracks) > 0:
                playlist_tracks += _tracks
            else:
                logger.warning(f'no tracks returned for {log_name} {username} / {playlist_name}')
        except SpotifyNetworkException:
            logger.exception(f'error occured while retrieving {log_name} {username} / {playlist_name}')

    playlist_tracks = list(remove_local(playlist_tracks))

    # LIBRARY
    if playlist.include_library_tracks:
        try:
            library_tracks = spotnet.saved_tracks()
            if library_tracks and len(library_tracks) > 0:
                playlist_tracks += library_tracks
            else:
                logger.error(f'error getting library tracks {username} / {playlist_name}')
        except SpotifyNetworkException:
            logger.exception(f'error occured while retrieving library tracks {username} / {playlist_name}')

    # PLAYLIST TYPE SPECIFIC
    if playlist.type == 'recents':
        boundary_date = datetime.datetime.now(datetime.timezone.utc) - \
                        datetime.timedelta(days=int(playlist.day_boundary))
        playlist_tracks = list(added_after(playlist_tracks, boundary_date))
    elif playlist.type == 'fmchart':
        if user.lastfm_username is None:
            logger.error(f'no associated last.fm username, chart source skipped {username} / {playlist_name}')
        else:
            chart_range = Network.Range.MONTH
            try:
                chart_range = Network.Range[playlist.chart_range]
            except KeyError:
                logger.error(f'invalid last.fm chart range found {playlist.chart_range}, '
                             f'defaulting to 1 month {username} / {playlist_name}')
            
            if fmnet is None:
                fmnet = database.get_authed_lastfm_network(user)

            if fmnet is not None:
                chart_tracks = map_lastfm_track_chart_to_spotify(spotnet=spotnet,
                                                                 fmnet=fmnet,
                                                                 period=chart_range,
                                                                 limit=playlist.chart_limit)

                if chart_tracks is not None and len(chart_tracks) > 0:
                    playlist_tracks += chart_tracks
                else:
                    logger.error(f'no tracks returned {username} / {playlist_name}')
            else:
                logger.error(f'no last.fm network returned {username} / {playlist_name}')

    # SORT METHOD
    if playlist.shuffle:
        random.shuffle(playlist_tracks)
    elif playlist.type != 'fmchart':
        playlist_tracks = sort_by_release_date(tracks=playlist_tracks, reverse=True)

    # RECOMMENDATIONS
    if playlist.include_recommendations:
        try:
            recommendations = spotnet.recommendations(tracks=[i.uri.object_id for i, j
                                                          in get_track_objects(
                                                                random.sample(playlist_tracks,
                                                                      k=min(5, len(playlist_tracks))
                                                                      )
                                                                )
                                                          if i.uri.object_type == Uri.ObjectType.track],
                                                  response_limit=playlist.recommendation_sample)
            if recommendations and len(recommendations.tracks) > 0:
                playlist_tracks += recommendations.tracks
            else:
                logger.error(f'error getting recommendations {username} / {playlist_name}')
        except SpotifyNetworkException:
            logger.exception(f'error occured while generating recommendations {username} / {playlist_name}')

    # DEDUPLICATE
    playlist_tracks = deduplicate_by_name(playlist_tracks)

    # EXECUTE
    try:
        spotnet.replace_playlist_tracks(uri=playlist.uri, uris=[i.uri for i, j in get_track_objects(playlist_tracks)])

        if playlist.description_overwrite:
            string = playlist.description_overwrite
        else:
            string = ' / '.join(sorted(part_names))

        if playlist.description_suffix:
            string += f' - {str(playlist.description_suffix)}'

        if string is None or len(string) == 0:
            logger.error(f'no string generated {username} / {playlist_name}')
            return None

        try:
            spotnet.change_playlist_details(uri=playlist.uri, description=string)
        except SpotifyNetworkException:
            logger.exception(f'error changing description for {username} / {playlist_name}')

    except SpotifyNetworkException:
        logger.exception(f'error executing {username} / {playlist_name}')

    playlist.last_updated = datetime.datetime.utcnow()
    playlist.update()
