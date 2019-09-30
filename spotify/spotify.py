from flask import Flask, render_template, redirect, request, session, flash, url_for
from google.cloud import firestore

import os

from spotify.auth import auth_blueprint
from spotify.api import api_blueprint, player_blueprint

db = firestore.Client()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'build'), template_folder="templates")
app.secret_key = db.collection(u'spotify').document(u'config').get().to_dict()['secret_key']
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(player_blueprint, url_prefix='/api/player')


@app.route('/')
def index():

    if 'username' in session:
        logged_in = True
        return redirect(url_for('app_route'))
    else:
        logged_in = False

    return render_template('login.html', logged_in=logged_in)


@app.route('/app', defaults={'path': ''})
@app.route('/app/<path:path>')
def app_route(path):

    if 'username' not in session:
        flash('please log in')
        return redirect(url_for('index'))

    return render_template('app.html')

# [END gae_python37_app]
