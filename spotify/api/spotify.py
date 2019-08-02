import requests
from base64 import b64encode
from google.cloud import firestore

db = firestore.Client()


def create_playlist(username, name):

    users = [i for i in db.collection(u'spotify_users').where(u'username', u'==', username).stream()]

    if len(users) == 1:

        user_dict = users[0].to_dict()
        spotify_keys = db.document('key/spotify').get().to_dict()

        idsecret = b64encode(bytes(spotify_keys['clientid'] + ':' + spotify_keys['clientsecret'], "utf-8")).decode("ascii")

        token_headers = {'Authorization': 'Basic %s' % idsecret}
        headers = {"Content-Type": "application/json"}

        data = {"grant_type": "refresh_token", "refresh_token": user_dict['refresh_token']}

        token_req = requests.post('https://accounts.spotify.com/api/token', data=data, headers=token_headers)

        if 200 <= token_req.status_code < 300:
            accesstoken = token_req.json()['access_token']

            json = {"name": name, "public": True, "collaborative": False}

            headers['Authorization'] = 'Bearer ' + accesstoken

            info_id = requests.get('https://api.spotify.com/v1/me', headers=headers).json()['id']

            play_req = requests.post(f'https://api.spotify.com/v1/users/{info_id}/playlists', json=json, headers=headers)

            resp = play_req.json()

            return resp["id"]

        else:
            print(token_req.status_code)
            raise Exception('failed to get access token')
