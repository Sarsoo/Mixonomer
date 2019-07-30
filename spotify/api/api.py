from flask import Blueprint, session, request, jsonify
from google.cloud import firestore
from werkzeug.security import check_password_hash, generate_password_hash

blueprint = Blueprint('api', __name__)
db = firestore.Client()


@blueprint.route('/playlists', methods=['GET'])
def get_playlists():

    if 'username' in session:

        users = db.collection(u'spotify_users').where(u'username', u'==', session['username']).stream()

        users = [i for i in users]

        if len(users) == 1:
            playlists = db.document(u'spotify_users/{}'.format(users[0].id)).collection(u'playlists')
        else:
            error = {'error': 'multiple usernames?'}
            return jsonify(error), 500

        response = {
            'playlists': [i.to_dict() for i in playlists.stream()]
        }

        return jsonify(response), 200

    else:
        error = {'error': 'not logged in'}
        return jsonify(error), 401


@blueprint.route('/playlist', methods=['GET', 'POST', 'PUT'])
def get_playlist():

    if 'username' in session:

        users = db.collection(u'spotify_users').where(u'username', u'==', session['username']).stream()

        users = [i for i in users]

        if len(users) == 1:
            playlists = db.document(u'spotify_users/{}'.format(users[0].id)).collection(u'playlists')
        else:
            error = {'error': 'multiple usernames?'}
            return jsonify(error), 500

        if request.method == 'GET':
            playlist_name = request.args.get('name', None)

            if playlist_name:

                playlist = [i for i in playlists.where(u'name', u'==', playlist_name).stream()]

                if len(playlist) == 0:
                    return jsonify({'error': 'no playlist found'}), 404
                elif len(playlist) > 1:
                    return jsonify({'error': 'multiple playlists found'}), 500

                return jsonify(playlist[0].to_dict()), 200

            else:
                response = {"error": 'no name requested'}
                return jsonify(response), 400

        elif request.method == 'POST' or request.method == 'PUT':

            request_json = request.get_json()

            if 'name' not in request_json:
                return jsonify({'error': "no name provided"}), 400

            playlist_name = request_json['name']

            return 404

    else:
        error = {'error': 'not logged in'}
        return jsonify(error), 401


@blueprint.route('/user', methods=['GET'])
def user():

    if 'username' in session:

        users = db.collection(u'spotify_users').where(u'username', u'==', session['username']).stream()
        users = [i for i in users]

        if len(users) == 1:
            pulled_user = db.collection(u'spotify_users').document(u'{}'.format(users[0].id)).get()
        else:
            error = {'error': 'multiple usernames?'}
            return jsonify(error), 500

        doc = pulled_user.to_dict()

        response = {
            'username': doc['username'],
            'type': doc['type'],
            'validated': doc['validated']
        }

        return jsonify(response), 200

    else:
        error = {'error': 'not logged in'}
        return jsonify(error), 401


@blueprint.route('/user/password', methods=['POST'])
def change_password():

    request_json = request.get_json()

    if 'username' in session:

        if 'new_password' in request_json and 'current_password' in request_json:

            if len(request_json['new_password']) == 0:
                response = {"error": 'zero length password'}
                return jsonify(response), 400

            if len(request_json['new_password']) > 30:
                response = {"error": 'password too long'}
                return jsonify(response), 400

            users = db.collection(u'spotify_users').where(u'username', u'==', session['username']).stream()
            users = [i for i in users]

            if len(users) == 1:
                current_user = db.collection(u'spotify_users').document(u'{}'.format(users[0].id))
            else:
                error = {'error': 'multiple usernames?'}
                return jsonify(error), 500

            if check_password_hash(current_user.get().to_dict()['password'], request_json['current_password']):

                current_user.update({'password': generate_password_hash(request_json['new_password'])})

                response = {"message": 'password changed', "status": "success"}
                return jsonify(response), 200

            else:
                error = {'error': 'wrong password provided'}
                return jsonify(error), 403

        else:
            error = {'error': 'malformed request, no old_password/new_password'}
            return jsonify(error), 400

    else:
        error = {'error': 'not logged in'}
        return jsonify(error), 401


@blueprint.route('/playlist', methods=['GET', 'PUT', 'POST'])
def playlist():
    return 401
