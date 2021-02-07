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