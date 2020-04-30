import functools
import logging

from flask import session, request, jsonify

from music.model.user import User

logger = logging.getLogger(__name__)


def is_logged_in():
    if 'username' in session:
        return True
    else:
        return False


def is_basic_authed():
    if request.authorization:
        if request.authorization.get('username', None) and request.authorization.get('password', None):
            user = User.collection.filter('username', '==', request.authorization.username.strip().lower()).get()
            if user is None:
                return False, None

            if user.check_password(request.authorization.password):
                return True, user
            else:
                return False, user

    return False, None


def login_required(func):
    @functools.wraps(func)
    def login_required_wrapper(*args, **kwargs):
        if is_logged_in():
            user = User.collection.filter('username', '==', session['username'].strip().lower()).get()
            return func(user=user, *args, **kwargs)
        else:
            logger.warning('user not logged in')
            return jsonify({'error': 'not logged in'}), 401
    return login_required_wrapper


def login_or_basic_auth(func):
    @functools.wraps(func)
    def login_or_basic_auth_wrapper(*args, **kwargs):
        if is_logged_in():
            user = User.collection.filter('username', '==', session['username'].strip().lower()).get()
            return func(user=user, *args, **kwargs)
        else:
            check, user = is_basic_authed()
            if check:
                return func(user=user, *args, **kwargs)
            else:
                logger.warning('user not logged in')
                return jsonify({'error': 'not logged in'}), 401

    return login_or_basic_auth_wrapper


def admin_required(func):
    @functools.wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        db_user = kwargs.get('user')

        if db_user is not None:
            if db_user.type == 'admin':
                return func(*args, **kwargs)
            else:
                logger.warning(f'{db_user.username} not authorized')
                return jsonify({'status': 'error', 'message': 'unauthorized'}), 401
        else:
            logger.warning('user not logged in')
            return jsonify({'error': 'not logged in'}), 401

    return admin_required_wrapper


def spotify_link_required(func):
    @functools.wraps(func)
    def spotify_link_required_wrapper(*args, **kwargs):
        db_user = kwargs.get('user')

        if db_user is not None:
            if db_user.spotify_linked:
                return func(*args, **kwargs)
            else:
                logger.warning(f'{db_user.username} spotify not linked')
                return jsonify({'status': 'error', 'message': 'spotify not linked'}), 401
        else:
            logger.warning('user not logged in')
            return jsonify({'error': 'not logged in'}), 401

    return spotify_link_required_wrapper


def lastfm_username_required(func):
    @functools.wraps(func)
    def lastfm_username_required_wrapper(*args, **kwargs):
        db_user = kwargs.get('user')

        if db_user is not None:
            if db_user.lastfm_username and len(db_user.lastfm_username) > 0:
                return func(*args, **kwargs)
            else:
                logger.warning(f'no last.fm username for {db_user.username}')
                return jsonify({'status': 'error', 'message': 'no last.fm username'}), 401
        else:
            logger.warning('user not logged in')
            return jsonify({'error': 'not logged in'}), 401

    return lastfm_username_required_wrapper


def gae_cron(func):
    @functools.wraps(func)
    def gae_cron_wrapper(*args, **kwargs):

        if request.headers.get('X-Appengine-Cron', None):
            return func(*args, **kwargs)
        else:
            logger.warning('user not logged in')
            return jsonify({'status': 'error', 'message': 'unauthorised'}), 401

    return gae_cron_wrapper


def cloud_task(func):
    @functools.wraps(func)
    def cloud_task_wrapper(*args, **kwargs):

        if request.headers.get('X-AppEngine-QueueName', None):
            return func(*args, **kwargs)
        else:
            logger.warning('non tasks request')
            return jsonify({'status': 'error', 'message': 'unauthorised'}), 401

    return cloud_task_wrapper
