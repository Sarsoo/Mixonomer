from flask import Blueprint, jsonify, request
import logging

from music.api.decorators import login_or_basic_auth, lastfm_username_required, spotify_link_required
import music.db.database as database

from spotfm.maths.counter import Counter
from spotframework.model.uri import Uri

blueprint = Blueprint('spotfm-api', __name__)
logger = logging.getLogger(__name__)


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
