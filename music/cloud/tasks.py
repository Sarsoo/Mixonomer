import datetime
import json
import os
import logging

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from music.tasks.run_user_playlist import run_user_playlist
from music.tasks.refresh_lastfm_stats import refresh_lastfm_track_stats

from music.model.user import User
from music.model.playlist import Playlist
from music.model.tag import Tag

tasker = tasks_v2.CloudTasksClient()
task_path = tasker.queue_path('sarsooxyz', 'europe-west2', 'spotify-executions')

logger = logging.getLogger(__name__)


def update_all_user_playlists():
    """Create user playlist refresh task for all users"""

    seconds_delay = 0
    logger.info('running')

    for iter_user in User.collection.fetch():

        if iter_user.spotify_linked and not iter_user.locked:

            task = {
                'app_engine_http_request': {  # Specify the type of request.
                    'http_method': 'POST',
                    'relative_uri': '/api/playlist/run/user/task',
                    'body': iter_user.username.encode()
                }
            }

            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_delay)

            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)

            task['schedule_time'] = timestamp

            tasker.create_task(task_path, task)
            seconds_delay += 30


def update_playlists(username):
    """Refresh all playlists for given user, environment dependent"""

    user = User.collection.filter('username', '==', username.strip().lower()).get()

    if user is None:
        logger.error(f'user {username} not found')
        return

    playlists = Playlist.collection.parent(user.key).fetch()

    seconds_delay = 0
    logger.info(f'running {username}')

    for iterate_playlist in playlists:
        if iterate_playlist.uri is not None:

            if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                run_user_playlist_task(username, iterate_playlist.name, seconds_delay)
            else:
                run_user_playlist(user, iterate_playlist)

            seconds_delay += 6


def run_user_playlist_task(username, playlist_name, delay=0):
    """Create tasks for a users given playlist"""

    task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'relative_uri': '/api/playlist/run/task',
            'body': json.dumps({
                'username': username,
                'name': playlist_name
            }).encode()
        }
    }

    if delay > 0:

        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)

        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        # Add the timestamp to the tasks.
        task['schedule_time'] = timestamp

    tasker.create_task(task_path, task)


def refresh_all_user_playlist_stats():
    """"Create user playlist stats refresh task for all users"""

    seconds_delay = 0
    logger.info('running')

    for iter_user in User.collection.fetch():

        if iter_user.spotify_linked and iter_user.lastfm_username and \
                len(iter_user.lastfm_username) > 0 and not iter_user.locked:

            if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                refresh_user_stats_task(username=iter_user.username, delay=seconds_delay)
            else:
                refresh_user_playlist_stats(username=iter_user.username)

            seconds_delay += 2400

        else:
            logger.debug(f'skipping {iter_user.username}')


def refresh_user_playlist_stats(username):
    """Refresh all playlist stats for given user, environment dependent"""

    user = User.collection.filter('username', '==', username.strip().lower()).get()
    if user is None:
        logger.error(f'user {username} not found')
        return

    playlists = Playlist.collection.parent(user.key).fetch()

    seconds_delay = 0
    logger.info(f'running stats for {username}')

    if user.lastfm_username and len(user.lastfm_username) > 0:
        for playlist in playlists:
            if playlist.uri is not None:

                if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                    refresh_playlist_task(username, playlist.name, seconds_delay)
                else:
                    refresh_lastfm_track_stats(username, playlist.name)

                seconds_delay += 1200
    else:
        logger.error('no last.fm username')


def refresh_user_stats_task(username, delay=0):
    """Create user playlist stats refresh task"""

    task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'relative_uri': '/api/spotfm/playlist/refresh/user/task',
            'body': username.encode()
        }
    }

    if delay > 0:
        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)

        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        task['schedule_time'] = timestamp

    tasker.create_task(task_path, task)


def refresh_playlist_task(username, playlist_name, delay=0):
    """Create user playlist stats refresh tasks"""

    track_task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'relative_uri': '/api/spotfm/playlist/refresh/task/track',
            'body': json.dumps({
                'username': username,
                'name': playlist_name
            }).encode()
        }
    }
    if delay > 0:
        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        track_task['schedule_time'] = timestamp

    album_task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'relative_uri': '/api/spotfm/playlist/refresh/task/album',
            'body': json.dumps({
                'username': username,
                'name': playlist_name
            }).encode()
        }
    }
    d = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay + 180)
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(d)

    album_task['schedule_time'] = timestamp

    artist_task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'relative_uri': '/api/spotfm/playlist/refresh/task/artist',
            'body': json.dumps({
                'username': username,
                'name': playlist_name
            }).encode()
        }
    }
    d = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay + 360)
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(d)

    artist_task['schedule_time'] = timestamp

    tasker.create_task(task_path, track_task)
    tasker.create_task(task_path, album_task)
    tasker.create_task(task_path, artist_task)


def update_all_user_tags():
    """Create user tag refresh task sfor all users"""

    seconds_delay = 0
    logger.info('running')

    for iter_user in User.collection.fetch():

        if iter_user.lastfm_username and len(iter_user.lastfm_username) > 0 and not iter_user.locked:

            for tag in Tag.collection.parent(iter_user.key).fetch():

                task = {
                    'app_engine_http_request': {  # Specify the type of request.
                        'http_method': 'POST',
                        'relative_uri': '/api/tag/update/task',
                        'body': json.dumps({
                                    'username': iter_user.username,
                                    'tag_id': tag.tag_id
                                }).encode()
                    }
                }

                d = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_delay)

                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(d)

                task['schedule_time'] = timestamp

                tasker.create_task(task_path, task)
                seconds_delay += 10
