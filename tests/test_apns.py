import unittest
from unittest import skip

import jwt

from music.model.user import User
from music.notif.apns import get_token, send_notification, get_secret


class TestAPNS(unittest.TestCase):
    @skip
    def test_get_token(self):

        token = get_token()
        secret = get_secret()

        decoded = jwt.decode(token, secret, algorithms=['ES256'])
        token

    @skip
    def test_notification(self):

        for id in User.collection.filter('username', '==', 'andy').get().apns_tokens:
            notif = send_notification(id, "test")

            print(notif)


if __name__ == '__main__':
    unittest.main()
