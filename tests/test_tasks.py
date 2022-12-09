import unittest
from unittest.mock import Mock

from music.tasks.run_user_playlist import run_user_playlist
from music.tasks.update_tag import update_tag

class TestRunPlaylist(unittest.TestCase):
    
    def test_run_unknown_name(self):
        with self.assertRaises(NameError):
            run_user_playlist(user='unknown_name', playlist='test_playlist')

    def test_run_unknown_playlist(self):
        with self.assertRaises(NameError):
            run_user_playlist(user='test', playlist='test')

    def test_run_no_uri(self):
        with self.assertRaises(AttributeError):
            run_user_playlist(user='test', playlist='test_playlist')

    def test_run_no_network(self):
        with self.assertRaises(NameError):
            run_user_playlist(user='test', playlist='test_uri')

class TestRunTag(unittest.TestCase):
    
    def test_run_unknown_name(self):
        with self.assertRaises(NameError):
            update_tag(user='unknown_name', tag='test_tag')

    def test_run_unknown_tag(self):
        with self.assertRaises(NameError):
            update_tag(user='test', tag='unknown_tag')

    def test_run_no_service_username(self):
        with self.assertRaises(AttributeError):
            update_tag(user='test', tag='test_tag')

    def test_mocked_without_components(self):
        spotnet = Mock()
        fmnet = Mock()
        fmnet.user_scrobble_count.return_value = 10

        user_mock = Mock()
        user_mock.lastfm_username = 'test_username'
        user_mock.notify = False
        user_mock.notify_playlist_updates = False
        user_mock.notify_tag_updates = False
        user_mock.notify_admins = False

        tag_mock = Mock()
        tag_mock.time_objects = True
        tag_mock.artists = []
        tag_mock.albums = []
        tag_mock.tracks = []

        update_tag(user=user_mock, tag=tag_mock, spotnet=spotnet, fmnet=fmnet)

        tag_mock.update.assert_called_once()

    def test_mocked_artists(self):
        spotnet = Mock()
        fmnet = Mock()
        fmnet.user_scrobble_count.return_value = 10

        artist_mock = Mock()
        artist_mock.user_scrobbles = 10
        fmnet.artist.return_value = artist_mock

        user_mock = Mock()
        user_mock.lastfm_username = 'test_username'
        user_mock.notify = False
        user_mock.notify_playlist_updates = False
        user_mock.notify_tag_updates = False
        user_mock.notify_admins = False

        dict_mock = {'name': 'test_name'}

        tag_mock = Mock()
        tag_mock.time_objects = False
        tag_mock.artists = [dict_mock, dict_mock, dict_mock]
        tag_mock.albums = []
        tag_mock.tracks = []

        update_tag(user=user_mock, tag=tag_mock, spotnet=spotnet, fmnet=fmnet)

        tag_mock.update.assert_called_once()
        self.assertEqual(tag_mock.count, 30)
        self.assertEqual(tag_mock.proportion, 300)
        self.assertEqual(len(tag_mock.artists), 3)
        self.assertEqual(dict_mock['count'], 10)

    def test_mocked_albums(self):
        spotnet = Mock()
        fmnet = Mock()
        fmnet.user_scrobble_count.return_value = 10

        album_mock = Mock()
        album_mock.user_scrobbles = 10
        fmnet.album.return_value = album_mock

        user_mock = Mock()
        user_mock.lastfm_username = 'test_username'
        user_mock.notify = False
        user_mock.notify_playlist_updates = False
        user_mock.notify_tag_updates = False
        user_mock.notify_admins = False

        dict_mock = {'name': 'test_name', 'artist': 'test_artist'}

        tag_mock = Mock()
        tag_mock.time_objects = False
        tag_mock.artists = []
        tag_mock.albums = [dict_mock, dict_mock, dict_mock]
        tag_mock.tracks = []

        update_tag(user=user_mock, tag=tag_mock, spotnet=spotnet, fmnet=fmnet)

        tag_mock.update.assert_called_once()
        self.assertEqual(tag_mock.count, 30)
        self.assertEqual(tag_mock.proportion, 300)
        self.assertEqual(len(tag_mock.albums), 3)
        self.assertEqual(dict_mock['count'], 10)

    def test_mocked_tracks(self):
        spotnet = Mock()
        fmnet = Mock()
        fmnet.user_scrobble_count.return_value = 10

        track_mock = Mock()
        track_mock.user_scrobbles = 10
        fmnet.track.return_value = track_mock

        user_mock = Mock()
        user_mock.lastfm_username = 'test_username'
        user_mock.notify = False
        user_mock.notify_playlist_updates = False
        user_mock.notify_tag_updates = False
        user_mock.notify_admins = False

        dict_mock = {'name': 'test_name', 'artist': 'test_artist'}

        tag_mock = Mock()
        tag_mock.time_objects = False
        tag_mock.artists = []
        tag_mock.albums = []
        tag_mock.tracks = [dict_mock, dict_mock, dict_mock]

        update_tag(user=user_mock, tag=tag_mock, spotnet=spotnet, fmnet=fmnet)

        tag_mock.update.assert_called_once()
        self.assertEqual(tag_mock.count, 30)
        self.assertEqual(tag_mock.proportion, 300)
        self.assertEqual(len(tag_mock.tracks), 3)
        self.assertEqual(dict_mock['count'], 10)