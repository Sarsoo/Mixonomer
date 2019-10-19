import functools
import logging

from flask import session, request, jsonify

from music.db import database as database

logger = logging.getLogger(__name__)


def is_logged_in():
    if 'username' in session:
        return True
    else:
        return False


def is_basic_authed():
    if request.authorization:
        if request.authorization.get('username', None) and request.authorization.get('password', None):
            if database.check_user_password(request.authorization.username, request.authorization.password):
                return True

    return False


def login_required(func):
    @functools.wraps(func)
    def login_required_wrapper(*args, **kwargs):
        if is_logged_in():
            return func(username=session['username'], *args, **kwargs)
        else:
            logger.warning('user not logged in')
            return jsonify({'error': 'not logged in'}), 401
    return login_required_wrapper


def login_or_basic_auth(func):
    @functools.wraps(func)
    def login_or_basic_auth_wrapper(*args, **kwargs):
        if is_logged_in():
            return func(username=session['username'], *args, **kwargs)
        elif is_basic_authed():
            return func(username=request.authorization.username, *args, **kwargs)
        else:
            logger.warning('user not logged in')
            return jsonify({'error': 'not logged in'}), 401

    return login_or_basic_auth_wrapper


def admin_required(func):
    @functools.wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        user_dict = database.get_user_doc_ref(kwargs.get('username')).get().to_dict()

        if user_dict:
            if user_dict['type'] == 'admin':
                return func(*args, **kwargs)
            else:
                logger.warning(f'{user_dict["username"]} not authorized')
                return jsonify({'status': 'error', 'message': 'unauthorized'}), 401
        else:
            logger.warning('user not logged in')
            return jsonify({'error': 'not logged in'}), 401

    return admin_required_wrapper


def spotify_link_required(func):
    @functools.wraps(func)
    def spotify_link_required_wrapper(*args, **kwargs):
        user_dict = database.get_user_doc_ref(kwargs.get('username')).get().to_dict()

        if user_dict:
            if user_dict['spotify_linked']:
                return func(*args, **kwargs)
            else:
                logger.warning(f'{user_dict["username"]} spotify not linked')
                return jsonify({'status': 'error', 'message': 'spotify not linked'}), 401
        else:
            logger.warning('user not logged in')
            return jsonify({'error': 'not logged in'}), 401

    return spotify_link_required_wrapper


def lastfm_username_required(func):
    @functools.wraps(func)
    def lastfm_username_required_wrapper(*args, **kwargs):
        user_dict = database.get_user_doc_ref(kwargs.get('username')).get().to_dict()

        if user_dict:
            if user_dict.get('lastfm_username'):
                return func(*args, **kwargs)
            else:
                logger.warning(f'no last.fm username for {user_dict["username"]}')
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
