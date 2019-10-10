from flask import Blueprint, request, jsonify
import logging

from spotify.api.decorators import login_or_basic_auth, spotify_link_required
import spotify.db.database as database

from spotframework.engine.playlistengine import PlaylistEngine
from spotframework.model.uri import Uri

blueprint = Blueprint('spotify_api', __name__)
logger = logging.getLogger(__name__)


@blueprint.route('/sort', methods=['POST'])
@login_or_basic_auth
@spotify_link_required
def play(username=None):
    request_json = request.get_json()

    net = database.get_authed_spotify_network(username)
    engine = PlaylistEngine(net)

    reverse = request_json.get('reverse', False)

    if 'uri' in request_json:
        try:
            uri = Uri(request_json['uri'])
            engine.reorder_playlist_by_added_date(uri=uri, reverse=reverse)
        except ValueError:
            return jsonify({'error': "malformed uri provided"}), 400
    elif 'playlist_name' in request_json:
        engine.reorder_playlist_by_added_date(name=request_json.get('playlist_name'), reverse=reverse)
    else:
        return jsonify({'error': "no uris provided"}), 400

    return jsonify({'message': 'sorted', 'status': 'success'}), 200
