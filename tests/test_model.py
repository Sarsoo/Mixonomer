import unittest

from music.model.user import User

class TestUser(unittest.TestCase):

    def test_fetch_all(self):
        users = User.collection.fetch()
        self.assertIsNotNone(users)
        self.assertTrue(len([i for i in users]) > 0)

    def test_to_dict(self):
        users = [i for i in User.collection.fetch()]
        self.assertIsInstance(users[0].to_dict(), dict)

    def test_to_dict_filtered_keys(self):
        users = [i for i in User.collection.fetch()]

        for user in users:
            for key in ['password', 'access_token', 'refresh_token', 'token_expiry', 'id', 'key']:
                self.assertNotIn(key, user.to_dict())

    def test_get_playlist(self):
        test_user = User.collection.filter('username', '==', "test").get()

        test_playlist = test_user.get_playlist("test_playlist")
        self.assertIsNotNone(test_playlist)

    def test_get_playlist_all_returned(self):
        test_user = User.collection.filter('username', '==', "test").get()

        exact, matches = test_user.get_playlist("test_playlist", single_return=False)
        self.assertIsNotNone(exact)
        self.assertEqual(len(matches), 1)

    def test_get_playlist_wrong_case(self):
        test_user = User.collection.filter('username', '==', "test").get()

        test_playlist = test_user.get_playlist("TEST_PLAYLIST")
        self.assertIsNotNone(test_playlist)

    def test_get_playlist_wrong_case_not_exact(self):
        test_user = User.collection.filter('username', '==', "test").get()

        exact, matches = test_user.get_playlist("TEST_PLAYLIST", single_return=False)
        self.assertIsNone(exact)
        self.assertEqual(len(matches), 1)

    def test_get_playlist_missing_key(self):
        test_user = User.collection.filter('username', '==', "test").get()

        with self.assertRaises(NameError):
            test_playlist = test_user.get_playlist("test_playlist_missing")

    def test_get_playlist_missing_key_without_error(self):
        test_user = User.collection.filter('username', '==', "test").get()

        test_playlist = test_user.get_playlist("test_playlist_missing", raise_error=False)
        self.assertIsNone(test_playlist)