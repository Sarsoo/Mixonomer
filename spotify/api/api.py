from flask import Blueprint, session, request, jsonify
from google.cloud import firestore
from werkzeug.security import check_password_hash, generate_password_hash

import spotify.api.database as database

blueprint = Blueprint('api', __name__)
db = firestore.Client()


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
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/playlist', methods=['GET', 'POST', 'PUT'])
def get_playlist():

    if 'username' in session:

        user_ref = database.get_user_doc_ref(session['username'])
        playlists = database.get_user_playlists_collection(user_ref.id)

        if request.method == 'GET':
            playlist_name = request.args.get('name', None)

            if playlist_name:

                queried_playlist = [i for i in playlists.where(u'name', u'==', playlist_name).stream()]

                if len(queried_playlist) == 0:
                    return jsonify({'error': 'no playlist found'}), 404
                elif len(queried_playlist) > 1:
                    return jsonify({'error': 'multiple playlists found'}), 500

                return jsonify(queried_playlist[0].to_dict()), 200

            else:
                return jsonify({"error": 'no name requested'}), 400

        elif request.method == 'POST' or request.method == 'PUT':

            request_json = request.get_json()

            if 'name' not in request_json:
                return jsonify({'error': "no name provided"}), 400

            playlist_name = request_json['name']
            playlist_parts = request_json.get('parts', None)
            playlist_id = request_json.get('id', None)

            queried_playlist = [i for i in playlists.where(u'name', u'==', playlist_name).stream()]

            if request.method == 'PUT':

                if len(queried_playlist) != 0:
                    return jsonify({'error': 'playlist already exists'}), 400

                if playlist_parts is None or playlist_id is None:
                    return jsonify({'error': 'parts and id required'}), 400

                playlists.add({
                    'name': playlist_name,
                    'parts': playlist_parts,
                    'playlist_id': playlist_id
                })

                return jsonify({"message": 'playlist added', "status": "success"}), 200

            else:

                if len(queried_playlist) == 0:
                    return jsonify({'error': "playlist doesn't exist"}), 400

                if len(queried_playlist) > 1:
                    return jsonify({'error': "multiple playlists exist"}), 500

                if playlist_parts is None and playlist_id is None:
                    return jsonify({'error': "no chnages to make"}), 400

                playlist_doc = playlists.document(queried_playlist[0].id)

                dic = {}

                if playlist_parts:
                    dic['parts'] = playlist_parts

                if playlist_id:
                    dic['playlist_id'] = playlist_id

                playlist_doc.update(dic)

                return jsonify({"message": 'playlist updated', "status": "success"}), 200

    else:
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/user', methods=['GET'])
def user():

    if 'username' in session:

        pulled_user = database.get_user_doc_ref(session['username']).get().to_dict()

        response = {
            'username': pulled_user['username'],
            'type': pulled_user['type'],
            'spotify_linked': pulled_user['spotify_linked'],
            'validated': pulled_user['validated']
        }

        return jsonify(response), 200

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

                response = {"message": 'password changed', "status": "success"}
                return jsonify(response), 200

            else:
                return jsonify({'error': 'wrong password provided'}), 403

        else:
            return jsonify({'error': 'malformed request, no old_password/new_password'}), 400

    else:
        return jsonify({'error': 'not logged in'}), 401
