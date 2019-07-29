from flask import Blueprint, session, request, jsonify
from google.cloud import firestore

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

        docs = playlists.stream()

        response = {
            'playlists': [i.to_dict() for i in docs]
        }

        return jsonify(response)

    else:
        error = {'error': 'username not in session, not logged in?'}
        return jsonify(error), 500


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

        return jsonify(response)

    else:
        error = {'error': 'username not in session, not logged in?'}
        return jsonify(error), 404


@blueprint.route('/playlist', methods=['GET', 'PUT', 'POST'])
def playlist():
    return 404
