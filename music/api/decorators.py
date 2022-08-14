import functools
import logging

from flask import session, request, jsonify, make_response

from music.model.user import User
from music.auth.jwt_keys import validate_key

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


def is_jwt_authed():
    if request.headers.get('Authorization', None):

        unparsed = request.headers.get('Authorization')

        if unparsed.startswith('Bearer '):

            token = validate_key(unparsed.removeprefix('Bearer ').strip())

            if token is not None:
                return token


def login_required(func):
    @functools.wraps(func)
    def login_required_wrapper(*args, **kwargs):
        if is_logged_in():
            user = User.collection.filter('username', '==', session['username'].strip().lower()).get()
            return func(*args, user=user, **kwargs)
        else:
            logger.warning('user not logged in')
            return jsonify({'error': 'not logged in'}), 401
    return login_required_wrapper


def login_or_jwt(func):
    @functools.wraps(func)
    def login_or_jwt_wrapper(*args, **kwargs):
        if is_logged_in():
            user = User.collection.filter('username', '==', session['username'].strip().lower()).get()
            return func(*args, user=user, **kwargs)
        else:
            token = is_jwt_authed()
            if token is not None:
                user = User.collection.filter('username', '==', token['sub'].strip().lower()).get()
                
                if user is not None:
                    return func(*args, auth=token, user=user, **kwargs)
                else:
                    logger.warning(f'user {token["sub"]} not found')
                    return jsonify({'error': f'user {token["sub"]} not found'}), 404
            else:
                logger.warning('user not authorised')
                return jsonify({'error': 'not authorised'}), 401

    return login_or_jwt_wrapper

def jwt_required(func):
    @functools.wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        
        token = is_jwt_authed()
        if token is not None:
            user = User.collection.filter('username', '==', token['sub'].strip().lower()).get()

            if user is not None:
                return func(*args, auth=token, user=user, **kwargs)
            else:
                logger.warning(f'user {token["sub"]} not found')
                return jsonify({'error': f'user {token["sub"]} not found'}), 404
        else:
            logger.warning('user not authorised')
            return jsonify({'error': 'not authorised'}), 401

    return jwt_required_wrapper


def login_or_basic_auth(func):
    @functools.wraps(func)
    def login_or_basic_auth_wrapper(*args, **kwargs):
        if is_logged_in():
            user = User.collection.filter('username', '==', session['username'].strip().lower()).get()
            return func(*args, user=user, **kwargs)
        else:
            check, user = is_basic_authed()
            if check:
                return func(*args, user=user, **kwargs)
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


def validate_json(*expected_args):
    def decorator_validate_json(func):
        @functools.wraps(func)
        def wrapper_validate_json(*args, **kwargs):
            return check_dict(request_params=request.get_json(),
                              expected_args=expected_args,
                              func=func,
                              args=args, kwargs=kwargs)
        return wrapper_validate_json
    return decorator_validate_json


def validate_args(*expected_args):
    def decorator_validate_args(func):
        @functools.wraps(func)
        def wrapper_validate_args(*args, **kwargs):
            return check_dict(request_params=request.args,
                              expected_args=expected_args,
                              func=func,
                              args=args, kwargs=kwargs)
        return wrapper_validate_args
    return decorator_validate_args


def check_dict(request_params, expected_args, func, args, kwargs):
    for expected_arg in expected_args:
        if isinstance(expected_arg, tuple):
            arg_key = expected_arg[0]
        else:
            arg_key = expected_arg

        if arg_key not in request_params:
            return jsonify({'status': 'error', 'message': f'{arg_key} not provided'}), 400

        if isinstance(expected_arg, tuple):
            if not isinstance(request_params[arg_key], expected_arg[1]):
                return jsonify({'status': 'error', 'message': f'{arg_key} not of type {expected_arg[1]}'}), 400

    return func(*args, **kwargs)

def no_cache(func):
    @functools.wraps(func)
    def no_cache_wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)

        if isinstance(resp, str):
            resp = make_response(resp)

        if isinstance(resp, tuple):
            response = resp[0]
        else:
            response = resp

        if response is not None:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers['Cache-Control'] = 'public, max-age=0'

        return resp

    return no_cache_wrapper
