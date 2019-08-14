from google.cloud import firestore

from spotframework.net.user import User
from spotframework.net.network import Network

db = firestore.Client()


def create_playlist(username, name):

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', username).stream()]

    if len(users) == 1:

        user_dict = users[0].to_dict()
        spotify_keys = db.document('key/spotify').get().to_dict()

        net = Network(User(spotify_keys['clientid'],
                           spotify_keys['clientsecret'],
                           user_dict['access_token'],
                           user_dict['refresh_token']))

        resp = net.create_playlist(net.user.username, name)

        if 'id' in resp:
            return resp['id']
        else:
            raise Exception('Error creating playlist')

    else:
        raise ValueError('no/multiple username(s)')
