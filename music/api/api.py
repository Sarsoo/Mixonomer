from flask import Blueprint, session, request, jsonify

import os
import datetime
import json
import logging

from google.cloud import firestore
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from music.api.decorators import login_required, login_or_basic_auth, admin_required, gae_cron, cloud_task
from music.tasks.run_user_playlist import run_user_playlist as run_user_playlist
from music.tasks.play_user_playlist import play_user_playlist as play_user_playlist

import music.db.database as database

blueprint = Blueprint('api', __name__)
db = firestore.Client()

tasker = tasks_v2.CloudTasksClient()
task_path = tasker.queue_path('sarsooxyz', 'europe-west2', 'spotify-executions')

logger = logging.getLogger(__name__)


@blueprint.route('/playlists', methods=['GET'])
@login_or_basic_auth
def get_playlists(username=None):
    return jsonify({
        'playlists':  [i.to_dict() for i in database.get_user_playlists(username)]
    }), 200


@blueprint.route('/playlist', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_or_basic_auth
def playlist(username=None):

    user_playlists = database.get_user_playlists(username)

    user_ref = database.get_user(username).db_ref
    playlists = user_ref.collection(u'playlists')

    if request.method == 'GET' or request.method == 'DELETE':
        playlist_name = request.args.get('name', None)

        if playlist_name:

            queried_playlist = next((i for i in user_playlists if i.name == playlist_name), None)

            if queried_playlist is None:
                return jsonify({'error': 'no playlist found'}), 404

            if request.method == "GET":
                return jsonify(queried_playlist.to_dict()), 200

            elif request.method == 'DELETE':
                database.delete_playlist(username=username, name=playlist_name)
                return jsonify({"message": 'playlist deleted', "status": "success"}), 200

        else:
            return jsonify({"error": 'no name requested'}), 400

    elif request.method == 'POST' or request.method == 'PUT':

        request_json = request.get_json()

        if 'name' not in request_json:
            return jsonify({'error': "no name provided"}), 400

        playlist_name = request_json['name']

        playlist_parts = request_json.get('parts', None)

        playlist_references = []

        if request_json.get('playlist_references', None):
            if request_json['playlist_references'] != -1:
                for i in request_json['playlist_references']:

                    updating_playlist = database.get_playlist(username=username, name=i)
                    if updating_playlist is not None:
                        playlist_references.append(updating_playlist.db_ref)
                    else:
                        return jsonify({"message": f'managed playlist {i} not found', "status": "error"}), 400

        if len(playlist_references) == 0 and request_json.get('playlist_references', None) != -1:
            playlist_references = None

        playlist_uri = request_json.get('uri', None)
        playlist_shuffle = request_json.get('shuffle', None)
        playlist_type = request_json.get('type', None)

        playlist_day_boundary = request_json.get('day_boundary', None)
        playlist_add_this_month = request_json.get('add_this_month', None)
        playlist_add_last_month = request_json.get('add_last_month', None)

        playlist_library_tracks = request_json.get('include_library_tracks', None)

        playlist_recommendation = request_json.get('include_recommendations', None)
        playlist_recommendation_sample = request_json.get('recommendation_sample', None)

        playlist_chart_range = request_json.get('chart_range', None)
        playlist_chart_limit = request_json.get('chart_limit', None)

        queried_playlist = [i for i in playlists.where(u'name', u'==', playlist_name).stream()]

        if request.method == 'PUT':

            if len(queried_playlist) != 0:
                return jsonify({'error': 'playlist already exists'}), 400

            from music.tasks.create_playlist import create_playlist as create_playlist

            to_add = {
                'name': playlist_name,
                'parts': playlist_parts if playlist_parts is not None else [],
                'playlist_references': playlist_references if playlist_references is not None else [],
                'include_library_tracks': playlist_library_tracks if playlist_library_tracks is not None else False,
                'include_recommendations': playlist_recommendation if playlist_recommendation is not None else False,
                'recommendation_sample': playlist_recommendation_sample if playlist_recommendation_sample is not None else 10,
                'uri': None,
                'shuffle': playlist_shuffle if playlist_shuffle is not None else False,
                'type': playlist_type if playlist_type is not None else 'default'
            }

            if user_ref.get().to_dict()['spotify_linked']:
                new_playlist = create_playlist(username, playlist_name)
                to_add['uri'] = str(new_playlist.uri) if new_playlist is not None else None

            if playlist_type == 'recents':
                to_add['day_boundary'] = playlist_day_boundary if playlist_day_boundary is not None else 21
                to_add['add_this_month'] = playlist_add_this_month if playlist_add_this_month is not None else False
                to_add['add_last_month'] = playlist_add_last_month if playlist_add_last_month is not None else False

            if playlist_type == 'fmchart':
                to_add['chart_range'] = playlist_chart_range
                to_add['chart_limit'] = playlist_chart_limit if playlist_chart_limit is not None else 50

            playlists.document().set(to_add)
            logger.info(f'added {username} / {playlist_name}')

            return jsonify({"message": 'playlist added', "status": "success"}), 201

        elif request.method == 'POST':

            if len(queried_playlist) == 0:
                return jsonify({'error': "playlist doesn't exist"}), 400

            if len(queried_playlist) > 1:
                return jsonify({'error': "multiple playlists exist"}), 500

            updating_playlist = database.get_playlist(username=username, name=playlist_name)

            dic = {}

            if playlist_parts is not None:
                if playlist_parts == -1:
                    dic['parts'] = []
                else:
                    dic['parts'] = playlist_parts

            if playlist_references is not None:
                if playlist_references == -1:
                    dic['playlist_references'] = []
                else:
                    dic['playlist_references'] = playlist_references

            if playlist_uri is not None:
                dic['uri'] = playlist_uri

            if playlist_shuffle is not None:
                dic['shuffle'] = playlist_shuffle

            if playlist_day_boundary is not None:
                dic['day_boundary'] = playlist_day_boundary

            if playlist_add_this_month is not None:
                dic['add_this_month'] = playlist_add_this_month

            if playlist_add_last_month is not None:
                dic['add_last_month'] = playlist_add_last_month

            if playlist_library_tracks is not None:
                dic['include_library_tracks'] = playlist_library_tracks

            if playlist_recommendation is not None:
                dic['include_recommendations'] = playlist_recommendation

            if playlist_recommendation_sample is not None:
                dic['recommendation_sample'] = playlist_recommendation_sample

            if playlist_chart_range is not None:
                dic['chart_range'] = playlist_chart_range

            if playlist_chart_limit is not None:
                dic['chart_limit'] = playlist_chart_limit

            if playlist_type is not None:
                dic['type'] = playlist_type

                if playlist_type == 'fmchart':
                    dic['chart_range'] = 'YEAR'
                    dic['chart_limit'] = 50

            if len(dic) == 0:
                logger.warning(f'no changes to make for {username} / {playlist_name}')
                return jsonify({"message": 'no changes to make', "status": "error"}), 400

            updating_playlist.update_database(dic)
            logger.info(f'updated {username} / {playlist_name}')

            return jsonify({"message": 'playlist updated', "status": "success"}), 200


@blueprint.route('/user', methods=['GET', 'POST'])
@login_or_basic_auth
def user(username=None):

    if request.method == 'GET':

        database_user = database.get_user(username)
        return jsonify(database_user.to_dict()), 200

    else:

        db_user = database.get_user(username)

        if db_user.user_type != db_user.Type.admin:
            return jsonify({'status': 'error', 'message': 'unauthorized'}), 401

        request_json = request.get_json()

        if 'username' in request_json:
            username = request_json['username']

        actionable_user = database.get_user(username)

        if 'locked' in request_json:
            logger.info(f'updating lock {username} / {request_json["locked"]}')
            actionable_user.locked = request_json['locked']

        if 'spotify_linked' in request_json:
            logger.info(f'deauthing {username}')
            if request_json['spotify_linked'] is False:
                actionable_user.update_database({
                    'access_token': None,
                    'refresh_token': None,
                    'spotify_linked': False
                })

        if 'lastfm_username' in request_json:
            logger.info(f'updating lastfm username {username} -> {request_json["lastfm_username"]}')
            actionable_user.lastfm_username = request_json['lastfm_username']

        logger.info(f'updated {username}')

        return jsonify({'message': 'account updated', 'status': 'succeeded'}), 200


@blueprint.route('/users', methods=['GET'])
@login_or_basic_auth
@admin_required
def users(username=None):
    return jsonify({
        'accounts': [i.to_dict() for i in database.get_users()]
    }), 200


@blueprint.route('/user/password', methods=['POST'])
@login_required
def change_password(username=None):

    request_json = request.get_json()

    if 'new_password' in request_json and 'current_password' in request_json:

        if len(request_json['new_password']) == 0:
            return jsonify({"error": 'zero length password'}), 400

        if len(request_json['new_password']) > 30:
            return jsonify({"error": 'password too long'}), 400

        db_user = database.get_user(username)
        if db_user.check_password(request_json['current_password']):
            db_user.password = request_json['new_password']
            logger.info(f'password udpated {username}')

            return jsonify({"message": 'password changed', "status": "success"}), 200
        else:
            logger.warning(f"incorrect password {username}")
            return jsonify({'error': 'wrong password provided'}), 401

    else:
        return jsonify({'error': 'malformed request, no old_password/new_password'}), 400


@blueprint.route('/playlist/play', methods=['POST'])
@login_or_basic_auth
def play_playlist(username=None):

    request_json = request.get_json()

    request_parts = request_json.get('parts', None)
    request_playlist_type = request_json.get('playlist_type', 'default')
    request_playlists = request_json.get('playlists', None)
    request_shuffle = request_json.get('shuffle', False)
    request_include_recommendations = request_json.get('include_recommendations', True)
    request_recommendation_sample = request_json.get('recommendation_sample', 10)
    request_day_boundary = request_json.get('day_boundary', 10)
    request_add_this_month = request_json.get('add_this_month', False)
    request_add_last_month = request_json.get('add_last_month', False)

    request_device_name = request_json.get('device_name', None)

    logger.info(f'playing {username}')

    if (request_parts and len(request_parts) > 0) or (request_playlists and len(request_playlists) > 0):

        if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
            create_play_user_playlist_task(username,
                                           parts=request_parts,
                                           playlist_type=request_playlist_type,
                                           playlists=request_playlists,
                                           shuffle=request_shuffle,
                                           include_recommendations=request_include_recommendations,
                                           recommendation_sample=request_recommendation_sample,
                                           day_boundary=request_day_boundary,
                                           add_this_month=request_add_this_month,
                                           add_last_month=request_add_last_month,
                                           device_name=request_device_name)
        else:
            play_user_playlist(username,
                               parts=request_parts,
                               playlist_type=request_playlist_type,
                               playlists=request_playlists,
                               shuffle=request_shuffle,
                               include_recommendations=request_include_recommendations,
                               recommendation_sample=request_recommendation_sample,
                               day_boundary=request_day_boundary,
                               add_this_month=request_add_this_month,
                               add_last_month=request_add_last_month,
                               device_name=request_device_name)

        return jsonify({'message': 'execution requested', 'status': 'success'}), 200
    else:
        logger.error(f'no playlists/parts {username}')
        return jsonify({'error': 'insufficient playlist sources'}), 400


@blueprint.route('/playlist/play/task', methods=['POST'])
@cloud_task
def play_playlist_task():
    payload = request.get_data(as_text=True)
    if payload:
        payload = json.loads(payload)
        logger.info(f'playing {payload["username"]}')

        play_user_playlist(payload['username'],
                           parts=payload['parts'],
                           playlist_type=payload['playlist_type'],
                           playlists=payload['playlists'],
                           shuffle=payload['shuffle'],
                           include_recommendations=payload['include_recommendations'],
                           recommendation_sample=payload['recommendation_sample'],
                           day_boundary=payload['day_boundary'],
                           add_this_month=payload['add_this_month'],
                           add_last_month=payload['add_last_month'],
                           device_name=payload['device_name'])

        return jsonify({'message': 'executed playlist', 'status': 'success'}), 200


@blueprint.route('/playlist/run', methods=['GET'])
@login_or_basic_auth
def run_playlist(username=None):

    playlist_name = request.args.get('name', None)

    if playlist_name:

        if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
            create_run_user_playlist_task(username, playlist_name)
        else:
            run_user_playlist(username, playlist_name)

        return jsonify({'message': 'execution requested', 'status': 'success'}), 200

    else:
        logger.warning('no playlist requested')
        return jsonify({"error": 'no name requested'}), 400


@blueprint.route('/playlist/run/task', methods=['POST'])
@cloud_task
def run_playlist_task():

    payload = request.get_data(as_text=True)
    if payload:
        payload = json.loads(payload)

        logger.info(f'running {payload["username"]} / {payload["name"]}')

        run_user_playlist(payload['username'], payload['name'])

        return jsonify({'message': 'executed playlist', 'status': 'success'}), 200


@blueprint.route('/playlist/run/user', methods=['GET'])
@login_or_basic_auth
def run_user(username=None):

    db_user = database.get_user(username)
    if db_user.type == db_user.Type.admin:
        user_name = request.args.get('username', username)
    else:
        user_name = username

    execute_user(user_name)

    return jsonify({'message': 'executed user', 'status': 'success'}), 200


@blueprint.route('/playlist/run/user/task', methods=['POST'])
@cloud_task
def run_user_task():

    payload = request.get_data(as_text=True)
    if payload:
        execute_user(payload)
        return jsonify({'message': 'executed user', 'status': 'success'}), 200


@blueprint.route('/playlist/run/users', methods=['GET'])
@login_or_basic_auth
@admin_required
def run_users(username=None):

    execute_all_users()
    return jsonify({'message': 'executed all users', 'status': 'success'}), 200


@blueprint.route('/playlist/run/users/cron', methods=['GET'])
@gae_cron
def run_users_cron():

    execute_all_users()
    return jsonify({'status': 'success'}), 200


def execute_all_users():

    seconds_delay = 0
    logger.info('running')

    for iter_user in database.get_users():

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


def execute_user(username):

    playlists = database.get_user_playlists(username)

    seconds_delay = 0
    logger.info(f'running {username}')

    for iterate_playlist in playlists:
        if iterate_playlist.uri:

            if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                create_run_user_playlist_task(username, iterate_playlist.name, seconds_delay)
            else:
                run_playlist(username, iterate_playlist.name)

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
