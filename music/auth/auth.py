from flask import Blueprint, session, flash, request, redirect, url_for, render_template, jsonify
from werkzeug.security import generate_password_hash
from music.model.user import User
from music.model.config import Config
from music.auth.jwt_keys import generate_key

from urllib.parse import urlencode, urlunparse
import datetime
import logging
from base64 import b64encode
import requests

blueprint = Blueprint('authapi', __name__)

logger = logging.getLogger(__name__)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """Login route allowing retrieval of HTML page and submission of results

    Returns:
        HTTP Response: Home page redirect for GET, login request on POST
    """

    if request.method == 'POST':

        session.pop('username', None)

        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if username is None or password is None:
            flash('malformed request')
            return redirect(url_for('index'))

        user = User.collection.filter('username', '==', username.strip().lower()).get()

        if user is None:
            flash('user not found')
            return redirect(url_for('index'))

        if user.check_password(password):
            if user.locked:
                logger.warning(f'locked account attempt {username}')
                flash('account locked')
                return redirect(url_for('index'))

            user.last_login = datetime.datetime.utcnow()
            user.update()

            logger.info(f'success {username}')
            session['username'] = username
            return redirect(url_for('app_route'))
        else:
            logger.warning(f'failed attempt {username}')
            flash('incorrect password')
            return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))


@blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        logger.info(f'logged out {session["username"]}')
    session.pop('username', None)
    flash('logged out')
    return redirect(url_for('index'))

@blueprint.route('/token', methods=['POST'])
def jwt_token():
    """Generate JWT

    Returns:
        HTTP Response: token request on POST
    """

    request_json = request.get_json()

    username = request_json.get('username', None)
    password = request_json.get('password', None)

    if username is None or password is None:
        return jsonify({"message": 'username and password fields required', "status": "error"}), 400

    user = User.collection.filter('username', '==', username.strip().lower()).get()

    if user is None:
        return jsonify({"message": 'user not found', "status": "error"}), 404

    if user.check_password(password):
        if user.locked:
            logger.warning(f'locked account token attempt {username}')
            return jsonify({"message": 'user locked', "status": "error"}), 403

        user.last_login = datetime.datetime.utcnow()
        user.update()

        logger.info(f'generating token for {username}')

        token = generate_key(user)

        return jsonify({"token": token, "status": "success"}), 200
    else:
        logger.warning(f'failed token attempt {username}')
        return jsonify({"message": 'authentication failed', "status": "error"}), 401


@blueprint.route('/register', methods=['GET', 'POST'])
def register():

    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('register.html')
    else:

        username = request.form.get('username', None)
        password = request.form.get('password', None)
        password_again = request.form.get('password_again', None)

        if username is None or password is None or password_again is None:
            flash('malformed request')
            return redirect('authapi.register')

        username = username.lower()

        if password != password_again:
            flash('password mismatch')
            return redirect('authapi.register')

        if username in [i.username for i in
                        User.collection.fetch()]:
            flash('username already registered')
            return redirect('authapi.register')

        user = User()
        user.username = username
        user.password = generate_password_hash(password)
        user.last_login = datetime.datetime.utcnow()

        user.save()

        logger.info(f'new user {username}')
        session['username'] = username
        return redirect(url_for('authapi.auth'))


@blueprint.route('/spotify')
def auth():

    if 'username' in session:

        config = Config.collection.get("config/music-tools")
        params = urlencode(
            {
                'client_id': config.spotify_client_id,
                'response_type': 'code',
                'scope': 'playlist-modify-public playlist-modify-private playlist-read-private '
                         'user-read-playback-state user-modify-playback-state user-library-read',
                'redirect_uri': 'https://mixonomer.sarsoo.xyz/auth/spotify/token'
            }
        )

        return redirect(urlunparse(['https', 'accounts.spotify.com', 'authorize', '', params, '']))

    return redirect(url_for('index'))


@blueprint.route('/spotify/token')
def token():

    if 'username' in session:

        code = request.args.get('code', None)
        if code is None:
            flash('authorization failed')
            return redirect('app_route')
        else:
            config = Config.collection.get("config/music-tools")

            idsecret = b64encode(
                bytes(config.spotify_client_id + ':' + config.spotify_client_secret, "utf-8")
            ).decode("ascii")
            headers = {'Authorization': 'Basic %s' % idsecret}

            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'https://mixonomer.sarsoo.xyz/auth/spotify/token'
            }

            req = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)

            if 200 <= req.status_code < 300:

                resp = req.json()

                user = User.collection.filter('username', '==', session['username'].strip().lower()).get()

                user.access_token = resp['access_token']
                user.refresh_token = resp['refresh_token']
                user.last_refreshed = datetime.datetime.now(datetime.timezone.utc)
                user.token_expiry = resp['expires_in']
                user.spotify_linked = True

                user.update()

            else:
                flash('http error on token request')
                return redirect('app_route')

        return redirect('/app/settings/spotify')

    return redirect(url_for('index'))


@blueprint.route('/spotify/deauth')
def deauth():

    if 'username' in session:

        user = User.collection.filter('username', '==', session['username'].strip().lower()).get()

        user.access_token = None
        user.refresh_token = None
        user.last_refreshed = datetime.datetime.now(datetime.timezone.utc)
        user.token_expiry = None
        user.spotify_linked = False

        user.update()

        return redirect('/app/settings/spotify')

    return redirect(url_for('index'))
