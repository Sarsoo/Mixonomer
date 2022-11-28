from flask import Blueprint, jsonify, request
import logging
import json
import os

from music.api.decorators import admin_required, login_or_jwt, lastfm_username_required, \
    spotify_link_required, cloud_task, validate_args, no_locked_users
import music.db.database as database
from music.cloud.tasks import refresh_all_user_playlist_stats, refresh_user_playlist_stats, refresh_playlist_task
from music.tasks.refresh_lastfm_stats import refresh_lastfm_track_stats, \
    refresh_lastfm_album_stats, \
    refresh_lastfm_artist_stats

from spotfm.maths.counter import Counter
from spotframework.model.uri import Uri
from spotframework.net.network import SpotifyNetworkException

blueprint = Blueprint('spotfm-api', __name__)
logger = logging.getLogger(__name__)


@blueprint.route('/count', methods=['GET'])
@login_or_jwt
@spotify_link_required
@lastfm_username_required
@no_locked_users
def count(auth=None, user=None):

    playlist_name = request.args.get('playlist_name', None)

    if uri := request.args.get('uri') is None and playlist_name is None:
        return jsonify({'error': 'no input provided'}), 401

    if uri:
        try:
            uri = Uri(uri)
        except ValueError:
            return jsonify({'error': 'malformed uri provided'}), 401

    spotnet = database.get_authed_spotify_network(user)
    fmnet = database.get_authed_lastfm_network(user)
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
        try:
            playlists = spotnet.playlists()
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
        except SpotifyNetworkException:
            logger.exception(f'error occured during {user.username} playlists retrieval')
            return jsonify({'error': f'playlist {playlist_name} not found'}), 404


@blueprint.route('/playlist/refresh', methods=['GET'])
@login_or_jwt
@spotify_link_required
@lastfm_username_required
@no_locked_users
@validate_args(('name', str))
def playlist_refresh(auth=None, user=None):

    playlist_name = request.args['name']

    if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
        refresh_playlist_task(user.username, playlist_name)
    else:
        refresh_lastfm_track_stats(user.username, playlist_name)
        refresh_lastfm_album_stats(user.username, playlist_name)
        refresh_lastfm_artist_stats(user.username, playlist_name)

    return jsonify({'message': 'execution requested', 'status': 'success'}), 200


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
@login_or_jwt
@admin_required
@no_locked_users
def run_users(auth=None, user=None):
    refresh_all_user_playlist_stats()
    return jsonify({'message': 'executed all users', 'status': 'success'}), 200


@blueprint.route('/playlist/refresh/user', methods=['GET'])
@login_or_jwt
@no_locked_users
def run_user(auth=None, user=None):

    if user.type == 'admin':
        user_name = request.args.get('username', user.username)
    else:
        user_name = user.username

    refresh_user_playlist_stats(user_name)

    return jsonify({'message': 'executed user', 'status': 'success'}), 200


@blueprint.route('/playlist/refresh/user/task', methods=['POST'])
@cloud_task
def run_user_task():

    payload = request.get_data(as_text=True)
    if payload:
        refresh_user_playlist_stats(payload)
        return jsonify({'message': 'executed user', 'status': 'success'}), 200
