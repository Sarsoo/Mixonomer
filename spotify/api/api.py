from flask import Blueprint, session, request, jsonify
from google.cloud import firestore
from google.cloud import pubsub_v1
from werkzeug.security import check_password_hash, generate_password_hash

import spotify.api.database as database

blueprint = Blueprint('api', __name__)
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()

run_playlist_topic_path = publisher.topic_path('sarsooxyz', 'run_user_playlist')


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

            queried_playlist = [i for i in playlists.where(u'name', u'==', playlist_name).stream()]

            if request.method == 'PUT':

                if len(queried_playlist) != 0:
                    return jsonify({'error': 'playlist already exists'}), 400

                # if playlist_id is None or playlist_shuffle is None:
                #     return jsonify({'error': 'parts and id required'}), 400

                from spotify.api.spotify import create_playlist as create_playlist

                to_add = {
                    'name': playlist_name,
                    'parts': playlist_parts if not None else [],
                    'playlist_references': playlist_references if not None else [],
                    'playlist_id': None,
                    'shuffle': playlist_shuffle,
                    'type': playlist_type
                }

                if user_ref.get().to_dict()['spotify_linked']:
                    new_playlist_id = create_playlist(session['username'], playlist_name)
                    to_add['playlist_id'] = new_playlist_id

                if playlist_type == 'recents':
                    to_add['day_boundary'] = playlist_day_boundary if playlist_day_boundary is not None else 21

                playlists.document().set(to_add)

                return jsonify({"message": 'playlist added', "status": "success"}), 200

            elif request.method == 'POST':

                if len(queried_playlist) == 0:
                    return jsonify({'error': "playlist doesn't exist"}), 400

                if len(queried_playlist) > 1:
                    return jsonify({'error': "multiple playlists exist"}), 500

                if playlist_parts is None and \
                        playlist_references is None and \
                        playlist_id is None and \
                        playlist_shuffle is None and \
                        playlist_day_boundary is None:
                    return jsonify({'error': "no chnages to make"}), 400

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

                if playlist_id:
                    dic['playlist_id'] = playlist_id

                if playlist_shuffle is not None:
                    dic['shuffle'] = playlist_shuffle

                if playlist_day_boundary is not None:
                    dic['day_boundary'] = playlist_day_boundary

                playlist_doc.update(dic)

                return jsonify({"message": 'playlist updated', "status": "success"}), 200

    else:
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

            dic = {}

            if 'locked' in request_json:
                dic['locked'] = request_json['locked']

            if len(dic) > 0:
                actionable_user.update(dic)

            return jsonify({'message': 'account locked', 'status': 'succeeded'}), 200

    else:
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

        return jsonify(dic)

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


@blueprint.route('/playlist/run', methods=['GET'])
def run_playlist():

    if 'username' in session:

        playlist_name = request.args.get('name', None)

        if playlist_name:

            execute_playlist(session['username'], playlist_name)

            return jsonify({'message': 'execution requested', 'status': 'success'}), 200

        else:
            return jsonify({"error": 'no name requested'}), 400

    else:
        return jsonify({'error': 'not logged in'}), 401


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
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/playlist/run/users', methods=['GET'])
def run_users():

    if 'username' in session:

        if database.get_user_doc_ref(session['username']).get().to_dict()['type'] != 'admin':
            return jsonify({'status': 'error', 'message': 'unauthorized'}), 401

        execute_all_users()

        return jsonify({'message': 'executed all users', 'status': 'success'}), 200

    else:
        return jsonify({'error': 'not logged in'}), 401


@blueprint.route('/playlist/run/users/cron', methods=['GET'])
def run_users_cron():

    if request.headers.get('X-Appengine-Cron'):
        execute_all_users()
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'unauthorised'}), 401


def execute_all_users():
    all_users = [i.to_dict() for i in db.collection(u'spotify_users').stream()]

    for iter_user in all_users:
        if iter_user['spotify_linked'] and not iter_user['locked']:
            execute_user(iter_user['username'])


def execute_user(username):

    playlists = [i.to_dict() for i in
                 database.get_user_playlists_collection(database.get_user_query_stream(username)[0].id).stream()]

    for iterate_playlist in playlists:
        if len(iterate_playlist['parts']) > 0 or len(iterate_playlist['playlist_references']) > 0:
            if iterate_playlist.get('playlist_id'):
                execute_playlist(username, iterate_playlist['name'])


def execute_playlist(username, name):

    data = u'{}'.format(name)
    data = data.encode('utf-8')

    publisher.publish(run_playlist_topic_path, data=data, username=username)
