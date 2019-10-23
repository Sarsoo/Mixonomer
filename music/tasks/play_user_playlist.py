from google.cloud import firestore

import datetime
import logging

from spotframework.engine.playlistengine import PlaylistEngine, PlaylistSource, RecommendationSource
from spotframework.engine.processor.shuffle import Shuffle
from spotframework.engine.processor.sort import SortReleaseDate
from spotframework.engine.processor.deduplicate import DeduplicateByID

from spotframework.player.player import Player
import music.db.database as database
from music.db.part_generator import PartGenerator

db = firestore.Client()

logger = logging.getLogger(__name__)


def play_user_playlist(username,
                       playlist_type='default',
                       parts=None,
                       playlists=None,
                       shuffle=False,
                       include_recommendations=True,
                       recommendation_sample=10,
                       day_boundary=10,
                       add_this_month=False,
                       add_last_month=False,
                       device_name=None):

    user = database.get_user(username)

    logger.info(f'playing for {username}')

    if user:

        if parts is None and playlists is None:
            logger.critical(f'no playlists to use for creation ({username})')
            return None

        if parts is None:
            parts = []

        if playlists is None:
            playlists = []

        if len(parts) == 0 and len(playlists) == 0:
            logger.critical(f'no playlists to use for creation ({username})')
            return None

        net = database.get_authed_spotify_network(username)

        device = None
        if device_name:
            devices = net.get_available_devices()
            if devices and len(devices) > 0:
                device = next((i for i in devices if i.name == device_name), None)
                if device is None:
                    logger.error(f'error selecting device {device_name} to play on')
            else:
                logger.warning(f'no available devices to play')

        engine = PlaylistEngine(net)

        player = Player(net)

        processors = [DeduplicateByID()]

        if shuffle:
            processors.append(Shuffle())
        else:
            processors.append(SortReleaseDate(reverse=True))

        submit_parts = parts

        part_generator = PartGenerator(user=user)

        for part in playlists:
            submit_parts += part_generator.get_recursive_parts(part)

        submit_parts = [i for i in {j for j in submit_parts}]

        params = [
            PlaylistSource.Params(names=submit_parts, processors=processors)
        ]

        if include_recommendations:
            params.append(RecommendationSource.Params(recommendation_limit=int(recommendation_sample)))

        if playlist_type == 'recents':
            boundary_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=int(day_boundary))
            tracks = engine.get_recent_playlist(params=params,
                                                boundary_date=boundary_date,
                                                add_this_month=add_this_month,
                                                add_last_month=add_last_month)
        else:
            tracks = engine.make_playlist(params=params)

        player.play(tracks=tracks, device=device)

    else:
        logger.critical(f'{username} not found')
