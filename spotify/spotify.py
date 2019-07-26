from flask import Flask, render_template, redirect
from google.cloud import firestore
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
            'redirect_uri': 'https://spotify.sarsoo.xyz/app'
        }
    )

    return redirect(urllib.parse.urlunparse(['https', 'accounts.spotify.com', 'authorize', '', params, '']))


@app.route('/app')
def app_route():
    return render_template('app.html')

# [END gae_python37_app]
