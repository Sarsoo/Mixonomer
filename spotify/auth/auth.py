from flask import Blueprint, session, flash, request, redirect, url_for
from google.cloud import firestore
from werkzeug.security import check_password_hash

import urllib
import datetime
from base64 import b64encode
import requests

import spotify.api.database as database

blueprint = Blueprint('authapi', __name__)

db = firestore.Client()


@blueprint.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        session.pop('username', None)

        username = request.form['username'].lower()
        password = request.form['password']

        users = database.get_user_query_stream(username)

        if len(users) == 0:
            flash('user not found')
            return redirect(url_for('index'))

        if len(users) > 1:
            flash('multiple users found')
            return redirect(url_for('index'))

        doc = users[0].to_dict()
        if doc is None:
            flash('username not found')
            return redirect(url_for('index'))

        if check_password_hash(doc['password'], password):

            user_reference = db.collection(u'spotify_users').document(u'{}'.format(users[0].id))
            user_reference.update({'last_login': datetime.datetime.utcnow()})

            session['username'] = username
            return redirect(url_for('app_route'))
        else:
            flash('incorrect password')
            return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))


@blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    flash('logged out')
    return redirect(url_for('index'))


@blueprint.route('/spotify')
def auth():

    if 'username' in session:

        client_id = db.document('key/spotify').get().to_dict()['clientid']
        params = urllib.parse.urlencode(
            {
                'client_id': client_id,
                'response_type': 'code',
                'scope': 'playlist-modify-public playlist-modify-private playlist-read-private',
                'redirect_uri': 'https://spotify.sarsoo.xyz/auth/spotify/token'
            }
        )

        return redirect(urllib.parse.urlunparse(['https', 'accounts.spotify.com', 'authorize', '', params, '']))

    return redirect('/')


@blueprint.route('/spotify/token')
def token():

    if 'username' in session:

        code = request.args.get('code', None)
        if code is None:
            error = request.args.get('error', None)
            print('error')
        else:
            app_credentials = db.document('key/spotify').get().to_dict()

            idsecret = b64encode(bytes(app_credentials['clientid'] + ':' + app_credentials['clientsecret'], "utf-8")).decode("ascii")
            headers = {'Authorization': 'Basic %s' % idsecret}

            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'https://spotify.sarsoo.xyz/auth/spotify/token'
            }

            req = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)

            resp = req.json()

            user_reference = database.get_user_doc_ref(session['username'])

            user_reference.update({
                'access_token': resp['access_token'],
                'refresh_token': resp['refresh_token'],
                'spotify_linked': True
            })

        return redirect('/app/settings/spotify')

    return redirect('/')


@blueprint.route('/spotify/deauth')
def deauth():

    if 'username' in session:

        user_reference = database.get_user_doc_ref(session['username'])

        user_reference.update({
            'access_token': None,
            'refresh_token': None,
            'spotify_linked': False
        })

        return redirect('/app/settings/spotify')

    return redirect('/')
