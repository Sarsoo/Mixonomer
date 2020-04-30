import datetime
import json
import os
import logging

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from music.db import database as database
from music.tasks.run_user_playlist import run_user_playlist
from music.tasks.refresh_lastfm_stats import refresh_lastfm_track_stats

from music.model.user import User
from music.model.playlist import Playlist

tasker = tasks_v2.CloudTasksClient()
task_path = tasker.queue_path('sarsooxyz', 'europe-west2', 'spotify-executions')

logger = logging.getLogger(__name__)


def execute_all_user_playlists():

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


def execute_user_playlists(username):
    user = User.collection.filter('username', '==', username.strip().lower()).get()

    if user is None:
        logger.error(f'user {username} not found')

    playlists = Playlist.collection.parent(user.key).fetch()

    seconds_delay = 0
    logger.info(f'running {username}')

    for iterate_playlist in playlists:
        if iterate_playlist.uri is not None:

            if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                create_run_user_playlist_task(username, iterate_playlist.name, seconds_delay)
            else:
                run_user_playlist(username, iterate_playlist.name)

            seconds_delay += 6


def create_run_user_playlist_task(username, playlist_name, delay=0):

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


def create_play_user_playlist_task(username,
                                   parts=None,
                                   playlist_type='default',
                                   playlists=None,
                                   shuffle=False,
                                   include_recommendations=False,
                                   recommendation_sample=10,
                                   day_boundary=10,
                                   add_this_month=False,
                                   add_last_month=False,
                                   delay=0,
                                   device_name=None):
    task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'relative_uri': '/api/playlist/play/task',
            'body': json.dumps({
                'username': username,
                'playlist_type': playlist_type,
                'parts': parts,
                'playlists': playlists,
                'shuffle': shuffle,
                'include_recommendations': include_recommendations,
                'recommendation_sample': recommendation_sample,
                'day_boundary': day_boundary,
                'add_this_month': add_this_month,
                'add_last_month': add_last_month,
                'device_name': device_name
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


def execute_all_user_playlist_stats():

    seconds_delay = 0
    logger.info('running')

    for iter_user in User.collection.fetch():

        if iter_user.spotify_linked and iter_user.lastfm_username and \
                len(iter_user.lastfm_username) > 0 and not iter_user.locked:

            if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                create_refresh_user_task(username=iter_user.username, delay=seconds_delay)
            else:
                execute_user_playlist_stats(username=iter_user.username)

            seconds_delay += 2400

        else:
            logger.debug(f'skipping {iter_user.username}')


def execute_user_playlist_stats(username):

    user = User.collection.filter('username', '==', username.strip().lower()).get()
    if user is None:
        logger.error(f'user {username} not found')

    playlists = Playlist.collection.parent(user.key).fetch()

    seconds_delay = 0
    logger.info(f'running {username}')

    if user.lastfm_username and len(user.lastfm_username) > 0:
        for playlist in playlists:
            if playlist.uri is not None:

                if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                    create_refresh_playlist_task(username, playlist.name, seconds_delay)
                else:
                    refresh_lastfm_track_stats(username, playlist.name)

                seconds_delay += 1200
    else:
        logger.error('no last.fm username')


def create_refresh_user_task(username, delay=0):

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


def create_refresh_playlist_task(username, playlist_name, delay=0):

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
