from flask import Blueprint, jsonify, request
import logging
import json
import os

from music.api.decorators import login_or_basic_auth, lastfm_username_required, spotify_link_required, cloud_task
import music.db.database as database
from music.tasks.refresh_lastfm_stats import refresh_lastfm_stats

from spotfm.maths.counter import Counter
from spotframework.model.uri import Uri

from google.cloud import tasks_v2

blueprint = Blueprint('spotfm-api', __name__)
logger = logging.getLogger(__name__)

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
            refresh_lastfm_stats(username, playlist_name)

        return jsonify({'message': 'execution requested', 'status': 'success'}), 200

    else:
        logger.warning('no playlist requested')
        return jsonify({"error": 'no name requested'}), 400


@blueprint.route('/playlist/refresh/task', methods=['POST'])
@cloud_task
def run_playlist_task():

    payload = request.get_data(as_text=True)
    if payload:
        payload = json.loads(payload)

        logger.info(f'running {payload["username"]} / {payload["name"]}')

        refresh_lastfm_stats(payload['username'], payload['name'])

        return jsonify({'message': 'executed playlist', 'status': 'success'}), 200


def create_refresh_playlist_task(username, playlist_name):

    task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'relative_uri': '/api/spotfm/playlist/refresh/task',
            'body': json.dumps({
                'username': username,
                'name': playlist_name
            }).encode()
        }
    }

    tasker.create_task(task_path, task)
