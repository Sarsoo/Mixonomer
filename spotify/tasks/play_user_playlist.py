from google.cloud import firestore

import datetime
import logging

from spotframework.engine.playlistengine import PlaylistEngine
from spotframework.engine.filter.shuffle import Shuffle
from spotframework.engine.filter.sortreversereleasedate import SortReverseReleaseDate
from spotframework.engine.filter.deduplicatebyid import DeduplicateByID

from spotframework.net.network import Network
from spotframework.net.user import User

db = firestore.Client()

captured_playlists = []

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

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', username).stream()]

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

        net = Network(User(spotify_keys['clientid'],
                           spotify_keys['clientsecret'],
                           user_dict['access_token'],
                           user_dict['refresh_token']))

        engine = PlaylistEngine(net)
        engine.load_user_playlists()

        processors = [DeduplicateByID()]

        if shuffle:
            processors.append(Shuffle())
        else:
            processors.append(SortReverseReleaseDate())

        global captured_playlists
        captured_playlists = []

        submit_parts = parts

        for part in playlists:
            submit_parts += generate_parts(users[0].id, part)

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

        net.play(uris=[i['uri'] for i in tracks])

    else:
        logger.critical(f'multiple/no user(s) found ({username})')
        return None


def generate_parts(user_id, name):

    playlist_doc = [i.to_dict() for i in
                    db.document(u'spotify_users/{}'.format(user_id))
                    .collection(u'playlists')
                    .where(u'name', '==', name).stream()][0]

    return_parts = playlist_doc['parts']

    captured_playlists.append(name)

    for i in playlist_doc['playlist_references']:
        if i not in captured_playlists:
            return_parts += generate_parts(user_id, i)

    return return_parts
