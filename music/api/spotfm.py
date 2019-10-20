from flask import Blueprint, jsonify, request
import logging
import json
import os
import datetime

from music.api.decorators import admin_required, login_or_basic_auth, lastfm_username_required, spotify_link_required, cloud_task, gae_cron
import music.db.database as database
from music.tasks.refresh_lastfm_stats import refresh_lastfm_track_stats, \
    refresh_lastfm_album_stats, \
    refresh_lastfm_artist_stats

from spotfm.maths.counter import Counter
from spotframework.model.uri import Uri

from google.cloud import firestore
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

blueprint = Blueprint('spotfm-api', __name__)
logger = logging.getLogger(__name__)

db = firestore.Client()
tasker = tasks_v2.CloudTasksClient()
task_path = tasker.queue_path('sarsooxyz', 'europe-west2', 'spotify-executions')


@blueprint.route('/count', methods=['GET'])
@login_or_basic_auth
@spotify_link_required
@lastfm_username_required
def count(username=None):

    uri = request.args.get('uri', None)
    playlist_name = request.args.get('playlist_name', None)

    if uri is None and playlist_name is None:
        return jsonify({'error': 'no input provided'}), 401

    if uri:
        try:
            uri = Uri(uri)
        except ValueError:
            return jsonify({'error': 'malformed uri provided'}), 401

    spotnet = database.get_authed_spotify_network(username)
    fmnet = database.get_authed_lastfm_network(username)
    counter = Counter(fmnet=fmnet, spotnet=spotnet)

    if uri:
        uri_count = counter.count(uri=uri)
        return jsonify({
            "uri": str(uri),
            "count": uri_count,
            'uri_type': str(uri.object_type),
            'last.fm_username': fmnet.username
        }), 200
    elif playlist_name:

        playlists = spotnet.get_playlists()
        playlist = next((i for i in playlists if i.name == playlist_name), None)

        if playlist is not None:
            playlist_count = counter.count_playlist(playlist=playlist)
            return jsonify({
                "count": playlist_count,
                'playlist_name': playlist_name,
                'last.fm_username': fmnet.username
            }), 200
        else:
            return jsonify({'error': f'playlist {playlist_name} not found'}), 404


@blueprint.route('/playlist/refresh', methods=['GET'])
@login_or_basic_auth
@spotify_link_required
@lastfm_username_required
def playlist_refresh(username=None):

    playlist_name = request.args.get('name', None)

    if playlist_name:

        if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
            create_refresh_playlist_task(username, playlist_name)
        else:
            refresh_lastfm_track_stats(username, playlist_name)
            refresh_lastfm_album_stats(username, playlist_name)
            refresh_lastfm_artist_stats(username, playlist_name)

        return jsonify({'message': 'execution requested', 'status': 'success'}), 200

    else:
        logger.warning('no playlist requested')
        return jsonify({"error": 'no name requested'}), 400


@blueprint.route('/playlist/refresh/task/track', methods=['POST'])
@cloud_task
def run_playlist_track_task():

    payload = request.get_data(as_text=True)
    if payload:
        payload = json.loads(payload)

        logger.info(f'refreshing tracks {payload["username"]} / {payload["name"]}')

        refresh_lastfm_track_stats(payload['username'], payload['name'])

        return jsonify({'message': 'executed playlist', 'status': 'success'}), 200


@blueprint.route('/playlist/refresh/task/album', methods=['POST'])
@cloud_task
def run_playlist_album_task():

    payload = request.get_data(as_text=True)
    if payload:
        payload = json.loads(payload)

        logger.info(f'refreshing albums {payload["username"]} / {payload["name"]}')

        refresh_lastfm_album_stats(payload['username'], payload['name'])

        return jsonify({'message': 'executed playlist', 'status': 'success'}), 200


@blueprint.route('/playlist/refresh/task/artist', methods=['POST'])
@cloud_task
def run_playlist_artist_task():

    payload = request.get_data(as_text=True)
    if payload:
        payload = json.loads(payload)

        logger.info(f'refreshing artists {payload["username"]} / {payload["name"]}')

        refresh_lastfm_artist_stats(payload['username'], payload['name'])

        return jsonify({'message': 'executed playlist', 'status': 'success'}), 200


@blueprint.route('/playlist/refresh/users', methods=['GET'])
@login_or_basic_auth
@admin_required
def run_users(username=None):
    execute_all_users()
    return jsonify({'message': 'executed all users', 'status': 'success'}), 200


@blueprint.route('/playlist/refresh/users/cron', methods=['GET'])
@gae_cron
def run_users_task():
    execute_all_users()
    return jsonify({'status': 'success'}), 200


@blueprint.route('/playlist/refresh/user', methods=['GET'])
@login_or_basic_auth
def run_user(username=None):

    if database.get_user_doc_ref(username).get().to_dict()['type'] == 'admin':
        user_name = request.args.get('username', username)
    else:
        user_name = username

    execute_user(user_name)

    return jsonify({'message': 'executed user', 'status': 'success'}), 200


@blueprint.route('/playlist/refresh/user/task', methods=['POST'])
@cloud_task
def run_user_task():

    payload = request.get_data(as_text=True)
    if payload:
        execute_user(payload)
        return jsonify({'message': 'executed user', 'status': 'success'}), 200


def execute_all_users():

    seconds_delay = 0
    logger.info('running')

    for iter_user in [i.to_dict() for i in db.collection(u'spotify_users').stream()]:

        if iter_user.get('spotify_linked') \
                and iter_user.get('lastfm_username') \
                and len(iter_user.get('lastfm_username')) > 0 \
                and not iter_user['locked']:

            if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                create_refresh_user_task(username=iter_user.get('username'), delay=seconds_delay)
            else:
                execute_user(username=iter_user.get('username'))

            seconds_delay += 2400

        else:
            logger.debug(f'skipping {iter_user.get("username")}')


def execute_user(username):

    playlists = [i.to_dict() for i in
                 database.get_user_playlists_collection(database.get_user_query_stream(username)[0].id).stream()]

    seconds_delay = 0
    logger.info(f'running {username}')

    user = database.get_user_doc_ref(username).get().to_dict()

    if user.get('lastfm_username') and len(user.get('lastfm_username')) > 0:
        for iterate_playlist in playlists:
            if iterate_playlist.get('uri', None):

                if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                    create_refresh_playlist_task(username, iterate_playlist['name'], seconds_delay)
                else:
                    refresh_lastfm_track_stats(username, iterate_playlist['name'])

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

        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        # Add the timestamp to the tasks.
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
