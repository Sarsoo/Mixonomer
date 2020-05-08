from google.cloud import firestore

import datetime
import logging

from spotframework.engine.playlistengine import PlaylistEngine, PlaylistSource, RecommendationSource, LibraryTrackSource
from spotframework.engine.processor.shuffle import Shuffle
from spotframework.engine.processor.sort import SortReleaseDate
from spotframework.engine.processor.deduplicate import DeduplicateByName
from spotframework.model.uri import Uri

from spotfm.engine.chart_source import ChartSource

from fmframework.net.network import Network

import music.db.database as database
from music.db.part_generator import PartGenerator
from music.model.user import User
from music.model.playlist import Playlist

db = firestore.Client()

logger = logging.getLogger(__name__)


def run_user_playlist(username, playlist_name):
    """Generate and upadate a user's playlist"""
    user = User.collection.filter('username', '==', username.strip().lower()).get()

    # PRE-RUN CHECKS
    if user is None:
        logger.error(f'user {username} not found')
        return

    logger.info(f'running {username} / {playlist_name}')

    playlist = Playlist.collection.parent(user.key).filter('name', '==', playlist_name).get()

    if playlist is None:
        logger.critical(f'playlist not found ({username}/{playlist_name})')
        return

    if playlist.uri is None:
        logger.critical(f'no playlist id to populate ({username}/{playlist_name})')
        return

    # END CHECKS

    net = database.get_authed_spotify_network(user)

    if net is None:
        logger.error(f'no spotify network returned for {username}')
        return

    engine = PlaylistEngine(net)
    part_generator = PartGenerator(user=user)

    spotify_playlist_names = part_generator.get_recursive_parts(playlist.name)

    processors = [DeduplicateByName()]
    params = [
        PlaylistSource.Params(names=spotify_playlist_names)
    ]

    # OPTIONS
    if playlist.include_recommendations:
        params.append(RecommendationSource.Params(recommendation_limit=playlist.recommendation_sample))

    if playlist.include_library_tracks:
        params.append(LibraryTrackSource.Params())
    # END OPTIONS

    if playlist.type == 'fmchart':
        if user.lastfm_username is None:
            logger.error(f'{username} has no associated last.fm username, chart source skipped')
        else:

            chart_range = Network.Range.MONTH
            try:
                chart_range = Network.Range[playlist.chart_range]
            except KeyError:
                logger.error(f'invalid last.fm chart range found for '
                             f'{playlist_name}/{username} {playlist.chart_range}, defaulting to 1 month')

            engine.sources.append(ChartSource(spotnet=net, fmnet=database.get_authed_lastfm_network(user)))
            params.append(ChartSource.Params(chart_range=chart_range, limit=playlist.chart_limit))

    else:
        # INCLUDE SORT METHOD (no sorting for last.fm chart playlist)
        if playlist.shuffle is True:
            processors.append(Shuffle())
        else:
            processors.append(SortReleaseDate(reverse=True))

    # GENERATE TRACKS
    if playlist.type == 'recents':
        boundary_date = datetime.datetime.now(datetime.timezone.utc) - \
                        datetime.timedelta(days=int(playlist.day_boundary))
        tracks = engine.get_recent_playlist(params=params,
                                            processors=processors,
                                            boundary_date=boundary_date,
                                            add_this_month=playlist.add_this_month,
                                            add_last_month=playlist.add_last_month)
    else:
        tracks = engine.make_playlist(params=params,
                                      processors=processors)

    # NET OPS
    engine.execute_playlist(tracks, Uri(playlist.uri))

    overwrite = playlist.description_overwrite
    suffix = playlist.description_suffix

    engine.change_description(sorted(spotify_playlist_names),
                              uri=Uri(playlist.uri),
                              overwrite=overwrite,
                              suffix=suffix)
    playlist.last_updated = datetime.datetime.utcnow()
    playlist.update()
