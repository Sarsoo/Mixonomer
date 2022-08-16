from flask import Blueprint, request, jsonify
from google.cloud import firestore
from werkzeug.security import generate_password_hash

import os
import json
import logging
from datetime import datetime

from music.api.decorators import login_or_jwt, login_required, login_or_jwt, \
    admin_required, cloud_task, validate_json, validate_args, spotify_link_required, no_locked_users
from music.cloud import queue_run_user_playlist, offload_or_run_user_playlist
from music.cloud.tasks import update_all_user_playlists, update_playlists

from music.tasks.create_playlist import create_playlist
from music.tasks.run_user_playlist import run_user_playlist

from music.model.user import User
from music.model.playlist import Playlist

import music.db.database as database

from spotframework.net.network import SpotifyNetworkException

blueprint = Blueprint('api', __name__)
db = firestore.Client()
logger = logging.getLogger(__name__)


@blueprint.route('/playlists', methods=['GET'])
@login_or_jwt
@no_locked_users
def all_playlists_route(auth=None, user=None):
    """Retrieve all playlists for a given user

    Args:
        user ([type], optional): [description]. Defaults to None.

    Returns:
        HTTP Response: All playlists for given user
    """

    assert user is not None
    return jsonify({
        'playlists': [i.to_dict() for i in Playlist.collection.parent(user.key).fetch()]
    }), 200


@blueprint.route('/playlist', methods=['GET', 'DELETE'])
@login_or_jwt
@no_locked_users
@validate_args(('name', str))
def playlist_get_delete_route(auth=None,user=None):

    playlist = user.get_playlist(request.args['name'], raise_error=False)

    if playlist is None:
        return jsonify({'error': f'playlist {request.args["name"]} not found'}), 404

    if request.method == "GET":
        return jsonify(playlist.to_dict()), 200

    elif request.method == 'DELETE':
        Playlist.collection.parent(user.key).delete(key=playlist.key)
        return jsonify({"message": 'playlist deleted', "status": "success"}), 200


@blueprint.route('/playlist', methods=['POST', 'PUT'])
@login_or_jwt
@no_locked_users
@validate_json(('name', str))
def playlist_post_put_route(auth=None, user=None):

    request_json = request.get_json()

    playlist_name = request_json['name']
    playlist_references = []

    if request_refs := request_json.get('playlist_references', None):
        if request_refs != -1:
            for i in request_refs:

                playlist = user.get_playlist(i, raise_error=False)
                if playlist is not None:
                    playlist_references.append(db.document(playlist.key))
                else:
                    return jsonify({"message": f'managed playlist {i} not found', "status": "error"}), 400

    if len(playlist_references) == 0 and request_refs != -1:
        playlist_references = None

    searched_playlist = user.get_playlist(playlist_name, raise_error=False)

    # CREATE
    if request.method == 'PUT':

        if searched_playlist is not None:
            return jsonify({'error': 'playlist already exists'}), 400

        playlist = Playlist(parent=user.key)

        playlist.name = request_json['name']

        for key in [i for i in Playlist.mutable_keys if i not in ['playlist_references', 'type']]:
            setattr(playlist, key, request_json.get(key, None))

        playlist.playlist_references = playlist_references

        playlist.last_updated = datetime.utcnow()
        playlist.lastfm_stat_last_refresh = datetime.utcnow()

        if request_json.get('type'):
            playlist_type = request_json['type'].strip().lower()
            if playlist_type in ['default', 'recents', 'fmchart']:
                playlist.type = playlist_type
            else:
                playlist.type = 'default'
                logger.warning(f'invalid type ({playlist_type}), {user.username} / {playlist_name}')

        if user.spotify_linked:
            new_playlist = create_playlist(user, playlist_name)
            playlist.uri = str(new_playlist.uri)

        playlist.save()
        logger.info(f'added {user.username} / {playlist_name}')

        return jsonify({"message": 'playlist added', "status": "success"}), 201

    # UPDATE
    elif request.method == 'POST':

        if searched_playlist is None:
            return jsonify({'error': "playlist doesn't exist"}), 400

        # ATTRIBUTES
        for rec_key, rec_item in request_json.items():
            # type and parts require extra validation
            if rec_key in [k for k in Playlist.mutable_keys if k not in ['type', 'parts', 'playlist_references']]:
                setattr(searched_playlist, rec_key, request_json[rec_key])

        # COMPONENTS
        if request_parts := request_json.get('parts'):
            if request_parts == -1:
                searched_playlist.parts = []
            else:
                searched_playlist.parts = request_parts

        if request_part_addition := request_json.get('add_part'):
            if request_part_addition not in searched_playlist.parts:
                searched_playlist.parts = searched_playlist.parts + [request_part_addition]

        if request_part_deletion := request_json.get('remove_part'):
            if request_part_deletion in searched_playlist.parts:
                searched_playlist.parts.remove(request_part_deletion)

        if playlist_references is not None:
            if playlist_references == -1:
                searched_playlist.playlist_references = []
            else:
                searched_playlist.playlist_references = playlist_references

        if request_ref_addition := request_json.get('add_ref'):
            playlist = user.get_playlist(request_ref_addition, raise_error=False)
            if playlist is not None and playlist.id not in [x.id for x in searched_playlist.playlist_references]:
                searched_playlist.playlist_references = searched_playlist.playlist_references + [db.document(playlist.key)]
            else:
                return jsonify({"message": f'managed playlist {request_ref_addition} not found', "status": "error"}), 400

        if request_ref_deletion := request_json.get('remove_ref'):
            playlist = user.get_playlist(request_ref_deletion, raise_error=False)
            if playlist is not None and playlist.id in [x.id for x in searched_playlist.playlist_references]:
                searched_playlist.playlist_references = [i for i in searched_playlist.playlist_references if i.id != playlist.id]
            else:
                return jsonify({"message": f'managed playlist {request_ref_deletion} not found', "status": "error"}), 400

        # ATTRIBUTE WITH CHECKS
        if request_type := request_json.get('type'):
            playlist_type = request_type.strip().lower()
            if playlist_type in ['default', 'recents', 'fmchart']:
                searched_playlist.type = playlist_type

        searched_playlist.update()
        logger.info(f'updated {user.username} / {playlist_name}')

        return jsonify({"message": 'playlist updated', "status": "success"}), 200

@blueprint.route('/user', methods=['GET', 'POST'])
@login_or_jwt
@no_locked_users
def user_route(auth=None, user=None):
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

            if user.lastfm_username is None:
                user.lastfm_username = ""

        user.update()

        logger.info(f'updated {user.username}')

        return jsonify({'message': 'account updated', 'status': 'succeeded'}), 200

@blueprint.route('/user', methods=['DELETE'])
@login_or_jwt
def user_delete_route(auth=None, user=None):
    assert user is not None

    if user.type == 'admin' and (username_override := request.args.get('username')) is not None:
        user = User.collection.filter('username', '==', username_override.strip().lower()).get()

    User.collection.delete(user.key, child=True)

    logger.info(f'user {user.username} deleted')

    return jsonify({'message': 'account deleted', 'status': 'succeeded'}), 200

@blueprint.route('/users', methods=['GET'])
@login_or_jwt
@admin_required
@no_locked_users
def all_users_route(auth=None, user=None):
    return jsonify({
        'accounts': [i.to_dict() for i in User.collection.fetch()]
    }), 200


@blueprint.route('/user/password', methods=['POST'])
@login_required
@no_locked_users
@validate_json(('new_password', str), ('current_password', str))
def change_password(user=None):
    request_json = request.get_json()

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


@blueprint.route('/playlist/run', methods=['GET'])
@login_or_jwt
@no_locked_users
@validate_args(('name', str))
def run_playlist(auth=None, user=None):

    if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
        queue_run_user_playlist(user.username, request.args['name'])  # pass to either cloud tasks or functions
    else:
        run_user_playlist(user, request.args['name'])  # update synchronously

    return jsonify({'message': 'execution requested', 'status': 'success'}), 200


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
@login_or_jwt
@no_locked_users
def run_user(auth=None, user=None):

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
@login_or_jwt
@admin_required
@no_locked_users
def run_users(auth=None, user=None):

    update_all_user_playlists()
    return jsonify({'message': 'executed all users', 'status': 'success'}), 200


@blueprint.route('/playlist/image', methods=['GET'])
@login_or_jwt
@spotify_link_required
@no_locked_users
@validate_args(('name', str))
def image(auth=None, user=None):

    _playlist = user.get_playlist(request.args['name'], raise_error=False)
    if _playlist is None:
        return jsonify({'error': "playlist not found"}), 404

    net = database.get_authed_spotify_network(user)

    try:
        return jsonify({'images': net.playlist(uri=_playlist.uri).images, 'status': 'success'}), 200
    except SpotifyNetworkException as e:
        logger.exception(f'error occured during {_playlist.name} / {user.username} playlist retrieval')
        return jsonify({'error': f"spotify error occured: {e.http_code}"}), 404
