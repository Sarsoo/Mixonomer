from google.cloud import firestore

import datetime
import logging

from spotframework.engine.playlistengine import PlaylistEngine
from spotframework.engine.processor.shuffle import Shuffle
from spotframework.engine.processor.sort import SortReleaseDate
from spotframework.engine.processor.deduplicate import DeduplicateByID

from spotframework.net.network import Network
from spotframework.net.user import NetworkUser
import spotify.db.database as database
from spotify.db.part_generator import PartGenerator

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
                       add_last_month=False):

    users = database.get_user_query_stream(username)

    logger.info(f'playing for {username}')

    if len(users) == 1:

        user_dict = users[0].to_dict()

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

        spotify_keys = db.document('key/spotify').get().to_dict()

        net = Network(NetworkUser(spotify_keys['clientid'],
                                  spotify_keys['clientsecret'],
                                  user_dict['access_token'],
                                  user_dict['refresh_token']))

        engine = PlaylistEngine(net)
        engine.load_user_playlists()

        processors = [DeduplicateByID()]

        if shuffle:
            processors.append(Shuffle())
        else:
            processors.append(SortReleaseDate(reverse=True))

        submit_parts = parts

        part_generator = PartGenerator(user_id=users[0].id)

        for part in playlists:
            submit_parts += part_generator.get_recursive_parts(part)

        submit_parts = [i for i in {j for j in submit_parts}]

        if playlist_type == 'recents':
            boundary_date = datetime.datetime.now() - datetime.timedelta(days=int(day_boundary))
            tracks = engine.get_recent_playlist(boundary_date,
                                                submit_parts,
                                                processors,
                                                include_recommendations=include_recommendations,
                                                recommendation_limit=int(recommendation_sample),
                                                add_this_month=add_this_month,
                                                add_last_month=add_last_month)
        else:
            tracks = engine.make_playlist(submit_parts,
                                          processors,
                                          include_recommendations=include_recommendations,
                                          recommendation_limit=int(recommendation_sample))

        net.play(uris=[i.uri for i in tracks])

    else:
        logger.critical(f'multiple/no user(s) found ({username})')
        return None
