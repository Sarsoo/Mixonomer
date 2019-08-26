from flask import Blueprint, session, request, jsonify

import os
import datetime
import json
import logging

from google.cloud import firestore
from google.cloud import pubsub_v1
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from werkzeug.security import check_password_hash, generate_password_hash

from spotify.tasks.run_user_playlist import run_user_playlist as run_user_playlist
from spotify.tasks.play_user_playlist import play_user_playlist as play_user_playlist

import spotify.db.database as database

blueprint = Blueprint('api', __name__)
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()

tasker = tasks_v2.CloudTasksClient()
task_path = tasker.queue_path('sarsooxyz', 'europe-west2', 'spotify-executions')
run_playlist_topic_path = publisher.topic_path('sarsooxyz', 'run_user_playlist')

logger = logging.getLogger(__name__)


@blueprint.route('/playlists', methods=['GET'])
def get_playlists():

    if 'username' in session:

        pulled_user = database.get_user_doc_ref(session['username'])

        playlists = database.get_user_playlists_collection(pulled_user.id)

        response = {
            'playlists': [i.to_dict() for i in playlists.stream()]
        }

        return jsonify(response), 200

    else:
        logger.warning('user not logged in')
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/playlist', methods=['GET', 'POST', 'PUT', 'DELETE'])
def playlist():

    if 'username' in session:

        user_ref = database.get_user_doc_ref(session['username'])
        playlists = database.get_user_playlists_collection(user_ref.id)

        if request.method == 'GET' or request.method == 'DELETE':
            playlist_name = request.args.get('name', None)

            if playlist_name:

                queried_playlist = [i for i in playlists.where(u'name', u'==', playlist_name).stream()]

                if len(queried_playlist) == 0:
                    return jsonify({'error': 'no playlist found'}), 404
                elif len(queried_playlist) > 1:
                    return jsonify({'error': 'multiple playlists found'}), 500

                if request.method == "GET":

                    return jsonify(queried_playlist[0].to_dict()), 200

                elif request.method == 'DELETE':

                    logger.info(f'deleted {session["username"]} / {queried_playlist[0].to_dict()["name"]}')
                    playlists.document(queried_playlist[0].id).delete()

                    return jsonify({"message": 'playlist deleted', "status": "success"}), 200

            else:
                return jsonify({"error": 'no name requested'}), 400

        elif request.method == 'POST' or request.method == 'PUT':

            request_json = request.get_json()

            if 'name' not in request_json:
                return jsonify({'error': "no name provided"}), 400

            playlist_name = request_json['name']

            playlist_parts = request_json.get('parts', None)
            playlist_references = request_json.get('playlist_references', None)

            playlist_id = request_json.get('id', None)
            playlist_shuffle = request_json.get('shuffle', None)
            playlist_type = request_json.get('type', None)

            playlist_day_boundary = request_json.get('day_boundary', None)
            playlist_add_this_month = request_json.get('add_this_month', None)
            playlist_add_last_month = request_json.get('add_last_month', None)

            playlist_recommendation = request_json.get('include_recommendations', None)
            playlist_recommendation_sample = request_json.get('recommendation_sample', None)

            queried_playlist = [i for i in playlists.where(u'name', u'==', playlist_name).stream()]

            if request.method == 'PUT':

                if len(queried_playlist) != 0:
                    return jsonify({'error': 'playlist already exists'}), 400

                # if playlist_id is None or playlist_shuffle is None:
                #     return jsonify({'error': 'parts and id required'}), 400

                from spotify.api.spotify import create_playlist as create_playlist

                to_add = {
                    'name': playlist_name,
                    'parts': playlist_parts if playlist_parts is not None else [],
                    'playlist_references': playlist_references if playlist_references is not None else [],
                    'include_recommendations': playlist_recommendation if playlist_recommendation is not None else False,
                    'recommendation_sample': playlist_recommendation_sample if playlist_recommendation_sample is not None else 10,
                    'playlist_id': None,
                    'shuffle': playlist_shuffle if playlist_shuffle is not None else False,
                    'type': playlist_type if playlist_type is not None else 'default'
                }

                if user_ref.get().to_dict()['spotify_linked']:
                    new_playlist_id = create_playlist(session['username'], playlist_name)
                    to_add['playlist_id'] = new_playlist_id

                if playlist_type == 'recents':
                    to_add['day_boundary'] = playlist_day_boundary if playlist_day_boundary is not None else 21
                    to_add['add_this_month'] = playlist_add_this_month if playlist_add_this_month is not None else False
                    to_add['add_last_month'] = playlist_add_last_month if playlist_add_last_month is not None else False

                playlists.document().set(to_add)
                logger.info(f'added {session["username"]} / {playlist_name}')

                return jsonify({"message": 'playlist added', "status": "success"}), 201

            elif request.method == 'POST':

                if len(queried_playlist) == 0:
                    return jsonify({'error': "playlist doesn't exist"}), 400

                if len(queried_playlist) > 1:
                    return jsonify({'error': "multiple playlists exist"}), 500

                playlist_doc = playlists.document(queried_playlist[0].id)

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

                if playlist_id is not None:
                    dic['playlist_id'] = playlist_id

                if playlist_shuffle is not None:
                    dic['shuffle'] = playlist_shuffle

                if playlist_day_boundary is not None:
                    dic['day_boundary'] = playlist_day_boundary

                if playlist_add_this_month is not None:
                    dic['add_this_month'] = playlist_add_this_month

                if playlist_add_last_month is not None:
                    dic['add_last_month'] = playlist_add_last_month

                if playlist_recommendation is not None:
                    dic['include_recommendations'] = playlist_recommendation

                if playlist_recommendation_sample is not None:
                    dic['recommendation_sample'] = playlist_recommendation_sample

                if playlist_type is not None:
                    dic['type'] = playlist_type

                if len(dic) == 0:
                    logger.warning(f'no changes to make for {session["username"]} / {playlist_name}')
                    return jsonify({"message": 'no changes to make', "status": "error"}), 400

                playlist_doc.update(dic)
                logger.info(f'updated {session["username"]} / {playlist_name}')

                return jsonify({"message": 'playlist updated', "status": "success"}), 200

    else:
        logger.warning('user not logged in')
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/user', methods=['GET', 'POST'])
def user():

    if 'username' in session:

        if request.method == 'GET':

            pulled_user = database.get_user_doc_ref(session['username']).get().to_dict()

            response = {
                'username': pulled_user['username'],
                'type': pulled_user['type'],
                'spotify_linked': pulled_user['spotify_linked'],
                'validated': pulled_user['validated']
            }

            return jsonify(response), 200

        else:

            if database.get_user_doc_ref(session['username']).get().to_dict()['type'] != 'admin':
                return jsonify({'status': 'error', 'message': 'unauthorized'}), 401

            request_json = request.get_json()

            if 'username' not in request_json:
                return jsonify({'status': 'error', 'message': 'no username provided'}), 400

            actionable_user = database.get_user_doc_ref(request_json['username'])

            if actionable_user.get().exists is False:
                return jsonify({"message": 'non-existent user', "status": "error"}), 400

            dic = {}

            if 'locked' in request_json:
                logger.info(f'updating lock {request_json["username"]} / {request_json["locked"]}')
                dic['locked'] = request_json['locked']

            if 'spotify_linked' in request_json:
                logger.info(f'deauthing {request_json["username"]}')
                if request_json['spotify_linked'] is False:
                    dic.update({
                        'access_token': None,
                        'refresh_token': None,
                        'spotify_linked': False
                    })

            if len(dic) == 0:
                logger.warning(f'no updates for {request_json["username"]}')
                return jsonify({"message": 'no changes to make', "status": "error"}), 400

            actionable_user.update(dic)
            logger.info(f'updated {request_json["username"]}')

            return jsonify({'message': 'account updated', 'status': 'succeeded'}), 200

    else:
        logger.warning('user not logged in')
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/users', methods=['GET'])
def users():

    if 'username' in session:

        if database.get_user_doc_ref(session['username']).get().to_dict()['type'] != 'admin':
            return jsonify({'status': 'unauthorised'}), 401

        dic = {
            'accounts': []
        }

        for account in [i.to_dict() for i in db.collection(u'spotify_users').stream()]:

            user_dic = {
                'username': account['username'],
                'type': account['type'],
                'spotify_linked': account['spotify_linked'],
                'locked': account['locked'],
                'last_login': account['last_login']
            }

            dic['accounts'].append(user_dic)

        return jsonify(dic), 200

    else:
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/user/password', methods=['POST'])
def change_password():

    request_json = request.get_json()

    if 'username' in session:

        if 'new_password' in request_json and 'current_password' in request_json:

            if len(request_json['new_password']) == 0:
                return jsonify({"error": 'zero length password'}), 400

            if len(request_json['new_password']) > 30:
                return jsonify({"error": 'password too long'}), 400

            current_user = database.get_user_doc_ref(session['username'])

            if check_password_hash(current_user.get().to_dict()['password'], request_json['current_password']):

                current_user.update({'password': generate_password_hash(request_json['new_password'])})
                logger.info(f'password udpated {session["username"]}')

                return jsonify({"message": 'password changed', "status": "success"}), 200

            else:
                logger.warning(f"incorrect password {session['username']}")
                return jsonify({'error': 'wrong password provided'}), 401

        else:
            return jsonify({'error': 'malformed request, no old_password/new_password'}), 400

    else:
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/playlist/play', methods=['POST'])
def play_playlist():

    if 'username' in session:

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

        logger.info(f'playing {session["username"]}')

        if request_parts or request_playlists:
            if len(request_parts) > 0 or len(request_playlists) > 0:

                if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                    create_play_user_playlist_task(session['username'],
                                                   parts=request_parts,
                                                   playlist_type=request_playlist_type,
                                                   playlists=request_playlists,
                                                   shuffle=request_shuffle,
                                                   include_recommendations=request_include_recommendations,
                                                   recommendation_sample=request_recommendation_sample,
                                                   day_boundary=request_day_boundary,
                                                   add_this_month=request_add_this_month,
                                                   add_last_month=request_add_last_month)
                else:
                    play_user_playlist(session['username'],
                                       parts=request_parts,
                                       playlist_type=request_playlist_type,
                                       playlists=request_playlists,
                                       shuffle=request_shuffle,
                                       include_recommendations=request_include_recommendations,
                                       recommendation_sample=request_recommendation_sample,
                                       day_boundary=request_day_boundary,
                                       add_this_month=request_add_this_month,
                                       add_last_month=request_add_last_month)

                return jsonify({'message': 'execution requested', 'status': 'success'}), 200

            else:
                logger.error(f'insufficient playlist/part lengths {session["username"]}')
                return jsonify({'error': 'insufficient playlist sources'}), 400

        else:
            logger.error(f'no playlists/parts {session["username"]}')
            return jsonify({'error': 'insufficient playlist sources'}), 400

    else:
        logger.warning('user not logged in')
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/playlist/play/task', methods=['POST'])
def play_playlist_task():
    if request.headers.get('X-AppEngine-QueueName', None):
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
                               add_last_month=payload['add_last_month'])

            return jsonify({'message': 'executed playlist', 'status': 'success'}), 200
    else:
        logger.warning('non tasks request')
        return jsonify({'error': 'unauthorized'}), 401


@blueprint.route('/playlist/run', methods=['GET'])
def run_playlist():

    if 'username' in session:

        playlist_name = request.args.get('name', None)

        if playlist_name:

            if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                create_run_user_playlist_task(session['username'], playlist_name)
            else:
                run_user_playlist(session['username'], playlist_name)

            return jsonify({'message': 'execution requested', 'status': 'success'}), 200

        else:
            logger.warning('no playlist requested')
            return jsonify({"error": 'no name requested'}), 400

    else:
        logger.warning('user not logged in')
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/playlist/run/task', methods=['POST'])
def run_playlist_task():

    if request.headers.get('X-AppEngine-QueueName', None):
        payload = request.get_data(as_text=True)
        if payload:
            payload = json.loads(payload)

            logger.info(f'running {payload["username"]} / {payload["name"]}')

            run_user_playlist(payload['username'], payload['name'])

            return jsonify({'message': 'executed playlist', 'status': 'success'}), 200
    else:
        logger.warning('non tasks request')
        return jsonify({'error': 'unauthorized'}), 401


@blueprint.route('/playlist/run/user', methods=['GET'])
def run_user():

    if 'username' in session:

        if database.get_user_doc_ref(session['username']).get().to_dict()['type'] == 'admin':
            user_name = request.args.get('username', session['username'])
        else:
            user_name = session['username']

        execute_user(user_name)

        return jsonify({'message': 'executed user', 'status': 'success'}), 200

    else:
        logger.warning('user not logged in')
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/playlist/run/user/task', methods=['POST'])
def run_user_task():

    if request.headers.get('X-AppEngine-QueueName', None):
        payload = request.get_data(as_text=True)
        if payload:
            execute_user(payload)
            return jsonify({'message': 'executed user', 'status': 'success'}), 200
    else:
        logger.warning('non tasks request')
        return jsonify({'error': 'unauthorized'}), 401


@blueprint.route('/playlist/run/users', methods=['GET'])
def run_users():

    if 'username' in session:

        if database.get_user_doc_ref(session['username']).get().to_dict()['type'] != 'admin':
            return jsonify({'status': 'error', 'message': 'unauthorized'}), 401

        execute_all_users()

        return jsonify({'message': 'executed all users', 'status': 'success'}), 200

    else:
        logger.warning('user not logged in')
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/playlist/run/users/cron', methods=['GET'])
def run_users_cron():

    if request.headers.get('X-Appengine-Cron', None):
        execute_all_users()
        return jsonify({'status': 'success'}), 200
    else:
        logger.warning('user not logged in')
        return jsonify({'status': 'error', 'message': 'unauthorised'}), 401


def execute_all_users():

    seconds_delay = 0
    logger.info('running')

    for iter_user in [i.to_dict() for i in db.collection(u'spotify_users').stream()]:

        if iter_user['spotify_linked'] and not iter_user['locked']:

            task = {
                'app_engine_http_request': {  # Specify the type of request.
                    'http_method': 'POST',
                    'relative_uri': '/api/playlist/run/user/task',
                    'body': iter_user['username'].encode()
                }
            }

            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds_delay)

            # Create Timestamp protobuf.
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)

            # Add the timestamp to the tasks.
            task['schedule_time'] = timestamp

            tasker.create_task(task_path, task)

            seconds_delay += 30


def execute_user(username):

    playlists = [i.to_dict() for i in
                 database.get_user_playlists_collection(database.get_user_query_stream(username)[0].id).stream()]

    seconds_delay = 0
    logger.info(f'running {username}')

    for iterate_playlist in playlists:
        if len(iterate_playlist['parts']) > 0 or len(iterate_playlist['playlist_references']) > 0:
            if iterate_playlist.get('playlist_id', None):

                if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
                    create_run_user_playlist_task(username, iterate_playlist['name'], seconds_delay)
                else:
                    run_playlist(username, iterate_playlist['name'])

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
                                   delay=0):
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
                'add_last_month': add_last_month
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


def push_run_user_playlist_message(username, name):

    data = u'{}'.format(name)
    data = data.encode('utf-8')

    publisher.publish(run_playlist_topic_path, data=data, username=username)
