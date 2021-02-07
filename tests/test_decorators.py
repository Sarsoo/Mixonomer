import os
import unittest
from unittest.mock import Mock

import flask

from music.music import create_app
from music.api.decorators import is_logged_in, admin_required, spotify_link_required, lastfm_username_required, check_dict, validate_json

class TestDecorators(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.test_app = self.app.test_client()

    ### LOGGED IN ###

    def test_is_logged_in_default_session(self):
        with self.app.test_request_context('/'):
            self.assertFalse('username' in flask.session)
            self.assertFalse(is_logged_in())

    def test_is_logged_in(self):
        with self.app.test_request_context('/'):
            flask.session['username'] = 'test'
            self.assertTrue('username' in flask.session)
            self.assertTrue(is_logged_in())

    ### ADMIN ###
    
    def test_admin_required(self):
        with self.app.test_request_context('/'):
            func = Mock()
            func.return_value = 5 # a known value to test for
            wrapped = admin_required(func)

            user_mock = Mock()
            user_mock.type = 'admin'
            resp = wrapped(user=user_mock)

            self.assertEqual(resp, 5)

    def test_admin_required_no_user(self):
        with self.app.test_request_context('/'):
            func = Mock()
            wrapped = admin_required(func)

            resp = wrapped()

            self.assertEqual(resp[1], 401)

    def test_admin_required_not_permitted(self):
        with self.app.test_request_context('/'):
            func = Mock()
            wrapped = admin_required(func)

            user_mock = Mock()
            user_mock.type = 'user'
            resp = wrapped(user=user_mock)

            self.assertEqual(resp[1], 401)

    ### SPOTIFY ###

    def test_spotify_required(self):
        with self.app.test_request_context('/'):
            func = Mock()
            func.return_value = 5 # a known value to test for
            wrapped = spotify_link_required(func)

            user_mock = Mock()
            user_mock.spotify_linked = True
            resp = wrapped(user=user_mock)

            self.assertEqual(resp, 5)

    def test_spotify_required_no_user(self):
        with self.app.test_request_context('/'):
            func = Mock()
            wrapped = spotify_link_required(func)

            resp = wrapped()

            self.assertEqual(resp[1], 401)

    def test_spotify_required_not_linked(self):
        with self.app.test_request_context('/'):
            func = Mock()
            wrapped = spotify_link_required(func)

            user_mock = Mock()
            user_mock.spotify_linked = False
            resp = wrapped(user=user_mock)

            self.assertEqual(resp[1], 401)

    ### LAST.FM ###

    def test_lastfm_required(self):
        with self.app.test_request_context('/'):
            func = Mock()
            func.return_value = 5 # a known value to test for
            wrapped = lastfm_username_required(func)

            user_mock = Mock()
            user_mock.lastfm_username = 'test_username'
            resp = wrapped(user=user_mock)

            self.assertEqual(resp, 5)

    def test_lastfm_required_no_user(self):
        with self.app.test_request_context('/'):
            func = Mock()
            wrapped = lastfm_username_required(func)

            resp = wrapped()

            self.assertEqual(resp[1], 401)

    def test_lastfm_required_zero_length(self):
        with self.app.test_request_context('/'):
            func = Mock()
            wrapped = lastfm_username_required(func)

            user_mock = Mock()
            user_mock.lastfm_username = ''
            resp = wrapped(user=user_mock)

            self.assertEqual(resp[1], 401)

    ### CHECK_DICT ###

    def test_check_dict(self):
        with self.app.test_request_context('/'):
            func = Mock()
            func.return_value = 5 # a known value to test for

            resp = check_dict(
                request_params=["test1", "test2", "test3"], 
                expected_args=["test1", "test2", "test3"], 
                func=func, 
                args=[], 
                kwargs={}
            )

            self.assertEqual(resp, 5)

    def test_check_dict_missing_required(self):
        with self.app.test_request_context('/'):
            func = Mock()
            func.return_value = 5 # a known value to test for

            resp = check_dict(
                request_params=["test1", "test2"], 
                expected_args=["test1", "test2", "test3"], 
                func=func, 
                args=[], 
                kwargs={}
            )

            self.assertEqual(resp[1], 400)
    
    def test_check_dict_tuples(self):
        with self.app.test_request_context('/'):
            func = Mock()
            func.return_value = 5 # a known value to test for

            resp = check_dict(
                request_params={"test1": 'hello world', "test2": 10, "test3": True}, 
                expected_args=[("test1", str), ("test2", int), ("test3", bool)], 
                func=func, 
                args=[], 
                kwargs={}
            )

            self.assertEqual(resp, 5)

    def test_check_dict_tuples_wrong_type(self):
        with self.app.test_request_context('/'):
            func = Mock()
            func.return_value = 5 # a known value to test for

            resp = check_dict(
                request_params={"test1": 'hello world', "test2": "hello world", "test3": True}, 
                expected_args=[("test1", str), ("test2", int), ("test3", bool)], 
                func=func, 
                args=[], 
                kwargs={}
            )

            self.assertEqual(resp[1], 400)