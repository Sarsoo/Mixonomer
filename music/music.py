from flask import Flask, render_template, redirect, session, flash, url_for
from google.cloud import secretmanager

import logging
import os

from music.auth import auth_blueprint
from music.api import api_blueprint, player_blueprint, fm_blueprint, \
    spotfm_blueprint, spotify_blueprint, admin_blueprint, tag_blueprint
from music.magic_strings import COOKIE_SECRET_URI, STATIC_BUCKET

logger = logging.getLogger(__name__)
secret_client = secretmanager.SecretManagerServiceClient()


def create_app():
    """Generate and retrieve a ready-to-run flask app

    Returns:
        Flask App: Mixonomer app
    """

    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'build'), template_folder="templates")

    app.secret_key = secret_client.access_secret_version(request={"name": COOKIE_SECRET_URI}).payload.data.decode("UTF-8")

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(player_blueprint, url_prefix='/api/player')
    app.register_blueprint(fm_blueprint, url_prefix='/api/fm')
    app.register_blueprint(spotfm_blueprint, url_prefix='/api/spotfm')
    app.register_blueprint(spotify_blueprint, url_prefix='/api/spotify')
    app.register_blueprint(admin_blueprint, url_prefix='/api/admin')
    app.register_blueprint(tag_blueprint, url_prefix='/api')

    @app.route('/')
    def index():

        if 'username' in session:
            logged_in = True
            return redirect('/app/playlists')
        else:
            logged_in = False

        return render_template('login.html', logged_in=logged_in, bucket=STATIC_BUCKET)

    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html', bucket=STATIC_BUCKET)

    @app.route('/app')
    def app_route_redirect():

        if 'username' not in session:
            flash('please log in')
            return redirect(url_for('index'))

        return redirect('/app/playlists')

    @app.route('/app/<path:path>')
    def app_route(path):

        if 'username' not in session:
            flash('please log in')
            return redirect(url_for('index'))

        return render_template('app.html', bucket=STATIC_BUCKET)

    return app

# [END gae_python37_app]
