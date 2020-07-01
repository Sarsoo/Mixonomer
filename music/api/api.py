from flask import Blueprint, request, jsonify
from google.cloud import firestore
from werkzeug.security import generate_password_hash

import os
import json
import logging
from datetime import datetime

from music.api.decorators import login_required, login_or_basic_auth, admin_required, gae_cron, cloud_task
from music.cloud import queue_run_user_playlist, offload_or_run_user_playlist
from music.cloud.tasks import update_all_user_playlists, update_playlists
from music.tasks.run_user_playlist import run_user_playlist

from music.model.user import User
from music.model.playlist import Playlist

import music.db.database as database

from spotframework.net.network import SpotifyNetworkException

blueprint = Blueprint('api', __name__)
db = firestore.Client()
logger = logging.getLogger(__name__)


@blueprint.route('/playlists', methods=['GET'])
@login_or_basic_auth
def all_playlists_route(user=None):
    assert user is not None
    return jsonify({
        'playlists':  [i.to_dict() for i in Playlist.collection.parent(user.key).fetch()]
    }), 200


@blueprint.route('/playlist', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_or_basic_auth
def playlist_route(user=None):

    if request.method == 'GET' or request.method == 'DELETE':
        playlist_name = request.args.get('name', None)

        if playlist_name:
            playlist = Playlist.collection.parent(user.key).filter('name', '==', playlist_name).get()

            if playlist is None:
                return jsonify({'error': f'playlist {playlist_name} not found'}), 404

            if request.method == "GET":
                return jsonify(playlist.to_dict()), 200

            elif request.method == 'DELETE':
                Playlist.collection.parent(user.key).delete(key=playlist.key)
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

                    updating_playlist = Playlist.collection.parent(user.key).filter('name', '==', i).get()
                    if updating_playlist is not None:
                        playlist_references.append(db.document(updating_playlist.key))
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

        playlist = Playlist.collection.parent(user.key).filter('name', '==', playlist_name).get()

        if request.method == 'PUT':

            if playlist is not None:
                return jsonify({'error': 'playlist already exists'}), 400

            from music.tasks.create_playlist import create_playlist

            new_db_playlist = Playlist(parent=user.key)

            new_db_playlist.name = playlist_name
            new_db_playlist.parts = playlist_parts
            new_db_playlist.playlist_references = playlist_references

            new_db_playlist.include_library_tracks = playlist_library_tracks
            new_db_playlist.include_recommendations = playlist_recommendation
            new_db_playlist.recommendation_sample = playlist_recommendation_sample

            new_db_playlist.shuffle = playlist_shuffle

            new_db_playlist.type = playlist_type
            new_db_playlist.last_updated = datetime.utcnow()
            new_db_playlist.lastfm_stat_last_refresh = datetime.utcnow()

            new_db_playlist.day_boundary = playlist_day_boundary
            new_db_playlist.add_this_month = playlist_add_this_month
            new_db_playlist.add_last_month = playlist_add_last_month

            new_db_playlist.chart_range = playlist_chart_range
            new_db_playlist.chart_limit = playlist_chart_limit

            if user.spotify_linked:
                new_playlist = create_playlist(user, playlist_name)
                new_db_playlist.uri = str(new_playlist.uri)

            new_db_playlist.save()
            logger.info(f'added {user.username} / {playlist_name}')

            return jsonify({"message": 'playlist added', "status": "success"}), 201

        elif request.method == 'POST':

            if playlist is None:
                return jsonify({'error': "playlist doesn't exist"}), 400

            updating_playlist = Playlist.collection.parent(user.key).filter('name', '==', playlist_name).get()

            if playlist_parts is not None:
                if playlist_parts == -1:
                    updating_playlist.parts = []
                else:
                    updating_playlist.parts = playlist_parts

            if playlist_references is not None:
                if playlist_references == -1:
                    updating_playlist.playlist_references = []
                else:
                    updating_playlist.playlist_references = playlist_references

            if playlist_uri is not None:
                updating_playlist.uri = playlist_uri

            if playlist_shuffle is not None:
                updating_playlist.shuffle = playlist_shuffle

            if playlist_day_boundary is not None:
                updating_playlist.day_boundary = playlist_day_boundary

            if playlist_add_this_month is not None:
                updating_playlist.add_this_month = playlist_add_this_month

            if playlist_add_last_month is not None:
                updating_playlist.add_last_month = playlist_add_last_month

            if playlist_library_tracks is not None:
                updating_playlist.include_library_tracks = playlist_library_tracks

            if playlist_recommendation is not None:
                updating_playlist.include_recommendations = playlist_recommendation

            if playlist_recommendation_sample is not None:
                updating_playlist.recommendation_sample = playlist_recommendation_sample

            if playlist_chart_range is not None:
                updating_playlist.chart_range = playlist_chart_range

            if playlist_chart_limit is not None:
                updating_playlist.chart_limit = playlist_chart_limit

            if playlist_type is not None:
                playlist_type = playlist_type.strip().lower()
                if playlist_type in ['default', 'recents', 'fmchart']:
                    updating_playlist.type = playlist_type

            updating_playlist.update()
            logger.info(f'updated {user.username} / {playlist_name}')

            return jsonify({"message": 'playlist updated', "status": "success"}), 200


@blueprint.route('/user', methods=['GET', 'POST'])
@login_or_basic_auth
def user_route(user=None):
    assert user is not None

    if request.method == 'GET':
        return jsonify(user.to_dict()), 200

    else:  # POST
        request_json = request.get_json()

        if 'username' in request_json:
            if request_json['username'].strip().lower() != user.username:
                if user.type != "admin":
                    return jsonify({'status': 'error', 'message': 'unauthorized'}), 401

                user = User.collection.filter('username', '==', request_json['username'].strip().lower()).get()

        if 'locked' in request_json:
            if user.type == "admin":
                logger.info(f'updating lock {user.username} / {request_json["locked"]}')
                user.locked = request_json['locked']

        if 'spotify_linked' in request_json:
            logger.info(f'deauthing {user.username}')
            if request_json['spotify_linked'] is False:
                user.access_token = None
                user.refresh_token = None
                user.spotify_linked = False

        if 'lastfm_username' in request_json:
            logger.info(f'updating lastfm username {user.username} -> {request_json["lastfm_username"]}')
            user.lastfm_username = request_json['lastfm_username']

        user.update()

        logger.info(f'updated {user.username}')

        return jsonify({'message': 'account updated', 'status': 'succeeded'}), 200


@blueprint.route('/users', methods=['GET'])
@login_or_basic_auth
@admin_required
def all_users_route(user=None):
    return jsonify({
        'accounts': [i.to_dict() for i in User.collection.fetch()]
    }), 200


@blueprint.route('/user/password', methods=['POST'])
@login_required
def change_password(user=None):
    request_json = request.get_json()

    if 'new_password' in request_json and 'current_password' in request_json:

        if len(request_json['new_password']) == 0:
            return jsonify({"error": 'zero length password'}), 400

        if len(request_json['new_password']) > 30:
            return jsonify({"error": 'password too long'}), 400

        if user.check_password(request_json['current_password']):
            user.password = generate_password_hash(request_json['new_password'])
            user.update()
            logger.info(f'password udpated {user.username}')

            return jsonify({"message": 'password changed', "status": "success"}), 200
        else:
            logger.warning(f"incorrect password {user.username}")
            return jsonify({'error': 'wrong password provided'}), 401

    else:
        return jsonify({'error': 'malformed request, no old_password/new_password'}), 400


@blueprint.route('/playlist/run', methods=['GET'])
@login_or_basic_auth
def run_playlist(user=None):

    playlist_name = request.args.get('name', None)

    if playlist_name:

        if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
            queue_run_user_playlist(user.username, playlist_name)  # pass to either cloud tasks or functions
        else:
            run_user_playlist(user.username, playlist_name)  # update synchronously

        return jsonify({'message': 'execution requested', 'status': 'success'}), 200

    else:
        logger.warning('no playlist requested')
        return jsonify({"error": 'no name requested'}), 400


@blueprint.route('/playlist/run/task', methods=['POST'])
@cloud_task
def run_playlist_task():  # receives cloud tasks request for update

    payload = request.get_data(as_text=True)
    if payload:
        payload = json.loads(payload)

        logger.info(f'running {payload["username"]} / {payload["name"]}')

        offload_or_run_user_playlist(payload['username'], payload['name'])  # check whether offloading to cloud function

        return jsonify({'message': 'executed playlist', 'status': 'success'}), 200

    logger.critical('no payload provided')


@blueprint.route('/playlist/run/user', methods=['GET'])
@login_or_basic_auth
def run_user(user=None):

    if user.type == 'admin':
        user_name = request.args.get('username', user.username)
    else:
        user_name = user.username

    update_playlists(user_name)

    return jsonify({'message': 'executed user', 'status': 'success'}), 200


@blueprint.route('/playlist/run/user/task', methods=['POST'])
@cloud_task
def run_user_task():

    payload = request.get_data(as_text=True)
    if payload:
        update_playlists(payload)
        return jsonify({'message': 'executed user', 'status': 'success'}), 200


@blueprint.route('/playlist/run/users', methods=['GET'])
@login_or_basic_auth
@admin_required
def run_users(user=None):

    update_all_user_playlists()
    return jsonify({'message': 'executed all users', 'status': 'success'}), 200


@blueprint.route('/playlist/run/users/cron', methods=['GET'])
@gae_cron
def run_users_cron():

    update_all_user_playlists()
    return jsonify({'status': 'success'}), 200


@blueprint.route('/playlist/image', methods=['GET'])
@login_or_basic_auth
def image(user=None):
    name = request.args.get('name', None)

    if name is None:
        return jsonify({'error': "no name provided"}), 400

    _playlist = Playlist.collection.parent(user.key).filter('name', '==', name).get()
    if _playlist is None:
        return jsonify({'error': "playlist not found"}), 404

    net = database.get_authed_spotify_network(user)

    try:
        return jsonify({'images': net.get_playlist(uri_string=_playlist.uri).images, 'status': 'success'}), 200
    except SpotifyNetworkException as e:
        logger.exception(f'error occured during {_playlist.name} / {user.username} playlist retrieval')
        return jsonify({'error': f"spotify error occured: {e.http_code}"}), 404
