from flask import Flask, render_template, redirect, request
from google.cloud import firestore
import requests

from base64 import b64encode

import os
import urllib

# Project ID is determined by the GCLOUD_PROJECT environment variable
db = firestore.Client()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'build'), template_folder="templates")

staticbucketurl = 'https://storage.googleapis.com/sarsooxyzstatic/'


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/auth')
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

        if 200 <= req.status_code < 300:
            resp = req.json()
            print(resp)

    return redirect('/app')


@app.route('/app')
@app.route('/app/<path>')
def app_route(path = None):
    return render_template('app.html')

# [END gae_python37_app]
