from google.cloud import firestore

import datetime
import logging

from spotframework.engine.playlistengine import PlaylistEngine, PlaylistSource, RecommendationSource, LibraryTrackSource
from spotframework.engine.processor.shuffle import Shuffle
from spotframework.engine.processor.sort import SortReleaseDate
from spotframework.engine.processor.deduplicate import DeduplicateByID

from spotframework.model.uri import Uri

import music.db.database as database
from music.db.part_generator import PartGenerator
from music.model.playlist import RecentsPlaylist

db = firestore.Client()

logger = logging.getLogger(__name__)


def run_user_playlist(username, playlist_name):
    user = database.get_user(username)

    logger.info(f'running {username} / {playlist_name}')

    if user:

        playlist = database.get_playlist(username=username, name=playlist_name)

        if playlist is not None:

            if playlist.uri is None:
                logger.critical(f'no playlist id to populate ({username}/{playlist_name})')
                return None

            if len(playlist.parts) == 0 and len(playlist.playlist_references) == 0:
                logger.critical(f'no playlists to use for creation ({username}/{playlist_name})')
                return None

            net = database.get_authed_spotify_network(username)

            engine = PlaylistEngine(net)

            processors = [DeduplicateByID()]

            if playlist.shuffle is True:
                processors.append(Shuffle())
            else:
                processors.append(SortReleaseDate(reverse=True))

            part_generator = PartGenerator(user=user)
            submit_parts = part_generator.get_recursive_parts(playlist.name)

            params = [
                PlaylistSource.Params(names=submit_parts)
            ]

            if playlist.include_recommendations:
                params.append(RecommendationSource.Params(recommendation_limit=playlist.recommendation_sample))

            if playlist.include_library_tracks:
                params.append(LibraryTrackSource.Params())

            if isinstance(playlist, RecentsPlaylist):
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

            engine.execute_playlist(tracks, Uri(playlist.uri))

            overwrite = playlist.description_overwrite
            suffix = playlist.description_suffix

            engine.change_description(sorted(submit_parts),
                                      uri=Uri(playlist.uri),
                                      overwrite=overwrite,
                                      suffix=suffix)

        else:
            logger.critical(f'playlist not found ({username}/{playlist_name})')
            return None

    else:
        logger.critical(f'{username} not found')
