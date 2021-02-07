import os
import unittest
from unittest.mock import patch

import flask

from music.music import create_app
import music.model.playlist

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.test_app = self.app.test_client()

    ### ROOT ###

    def test_root_route_without_login(self):
        response = self.test_app.get('/')
        self.assertTrue(199 < response.status_code <= 299)

    def test_root_route_with_login(self):
        with self.test_app.session_transaction() as sess:
            sess['username'] = 'test'
        response = self.test_app.get('/')
        self.assertTrue(299 < response.status_code <= 399)

    def test_app_route_redirects_without_login(self):
        response = self.test_app.get('/app')
        self.assertTrue(299 < response.status_code <= 399)

    def test_app_route_with_login(self):
        with self.test_app.session_transaction() as sess:
            sess['username'] = 'test'
        response = self.test_app.get('/app')
        self.assertTrue(199 < response.status_code <= 299)

    ### PLAYLISTS ###

    def test_all_playlists_route(self):
        with self.test_app.session_transaction() as sess:
            sess['username'] = 'andy'
        response = self.test_app.get('/api/playlists')

        self.assertTrue(199 < response.status_code <= 299)
        self.assertIsNotNone(response.get_json())
        self.assertTrue(len(response.get_json()['playlists']) > 0)

    def test_playlist_get(self):
        with self.test_app.session_transaction() as sess:
            sess['username'] = 'andy'
        response = self.test_app.get('/api/playlist?name=RAP')

        self.assertEqual(response.status_code, 200)

    def test_playlist_get_no_param(self):
        with self.test_app.session_transaction() as sess:
            sess['username'] = 'andy'
        response = self.test_app.get('/api/playlist')

        self.assertEqual(response.status_code, 400)

    def test_playlist_get_wrong_param(self):
        with self.test_app.session_transaction() as sess:
            sess['username'] = 'andy'
        response = self.test_app.get('/api/playlist?name=playlist_name')

        self.assertEqual(response.status_code, 404)

    #TODO: patch fireo so can test delete

    def test_playlist_delete_no_param(self):
        with self.test_app.session_transaction() as sess:
            sess['username'] = 'andy'
        response = self.test_app.delete('/api/playlist')

        self.assertEqual(response.status_code, 400)

    def test_playlist_delete_wrong_param(self):
        with self.test_app.session_transaction() as sess:
            sess['username'] = 'andy'
        response = self.test_app.delete('/api/playlist?name=playlist_name')

        self.assertEqual(response.status_code, 404)

    ### USERS ###
    def test_user_get(self):
        with self.test_app.session_transaction() as sess:
            sess['username'] = 'andy'
        response = self.test_app.get('/api/user')

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.get_json())

if __name__ == '__main__':
    unittest.main()