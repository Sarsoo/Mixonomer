from ast import Assert
from time import sleep
import unittest
from datetime import timedelta

from music.model.user import User
from music.auth.jwt_keys import generate_key, validate_key

class TestAuth(unittest.TestCase):

    def test_encode_decode(self):
        
        test_user = User.collection.filter('username', '==', "test").get()

        key = generate_key(test_user, timedelta(minutes=10))

        decoded = validate_key(key)

        self.assertEqual(decoded["sub"], test_user.username)

    def test_timeout(self):
        
        test_user = User.collection.filter('username', '==', "test").get()

        key = generate_key(test_user, timedelta(seconds=2))

        decoded = validate_key(key)
        self.assertIsNotNone(decoded)

        sleep(4)

        decoded = validate_key(key)
        self.assertIsNone(decoded)