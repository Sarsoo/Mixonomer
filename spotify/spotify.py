from flask import Flask, render_template, redirect, request, session, flash, url_for
from google.cloud import firestore
import requests

from base64 import b64encode

import os
import urllib

from spotify.auth import auth_blueprint
from spotify.api import api_blueprint

# Project ID is determined by the GCLOUD_PROJECT environment variable
db = firestore.Client()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'build'), template_folder="templates")
app.secret_key = db.collection(u'spotify').document(u'config').get().to_dict()['secret_key']
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(api_blueprint, url_prefix='/api')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/spotify/auth')
def auth():

    client_id = db.document('key/spotify').get().to_dict()['clientid']
    params = urllib.parse.urlencode(
        {
            'client_id': client_id,
            'response_type': 'code',
            'scope': 'playlist-modify-public playlist-modify-private playlist-read-private',
            'redirect_uri': 'https://spotify.sarsoo.xyz/token'
        }
    )

    return redirect(urllib.parse.urlunparse(['https', 'accounts.spotify.com', 'authorize', '', params, '']))


@app.route('/token')
def token():

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
            'redirect_uri': 'https://spotify.sarsoo.xyz/token'
        }

        req = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)

        resp = req.json()
        # print(str(req.status_code) + str(resp))

        # if 200 <= req.status_code < 300:

    return redirect('/app')


@app.route('/app', defaults={'path': ''})
@app.route('/app/<path:path>')
def app_route(path):

    if 'username' not in session:
        flash('please log in')
        return redirect(url_for('index'))

    return render_template('app.html')

# [END gae_python37_app]
